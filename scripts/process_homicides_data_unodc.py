import os
import logging
import pandas as pd
import polars as pl

# --- CONFIG & PATHS ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_PATH = os.path.join(SCRIPT_PATH, '..')
INPUT_DIR = os.path.join(PROJECT_PATH, 'data', 'raw')
OUTPUT_DIR = os.path.join(PROJECT_PATH, 'data', 'processed')

INPUT_FILE = os.path.join(INPUT_DIR, 'data_cts_intentional_homicide.xlsx')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'processed_unodc_intentional_homicide_rate.csv')

# Filters
TARGET_INDICATOR = 'Victims of intentional homicide'
#TARGET_UNIT = 'Rate per 100,000 population'
TARGET_SHEET = 'data_cts_intentional_homicide'
COLS_REMOVE = ['Iso3_code', 'Indicator', 'Source']

def main():
    try:
        logger.info(f"📂 Processing file: {INPUT_FILE}")

        # 1. Read Excel with Pandas (Handling header offset)
        # Using openpyxl engine implicitly
        pdf = pd.read_excel(
            INPUT_FILE, 
            sheet_name=TARGET_SHEET, 
            header=2
        )

        # 2. Convert to Polars for speed
        df = pl.from_pandas(pdf)

        # 3. Data processing
        logger.info("🧹 Processing the data...")

        df = df.filter(
            (pl.col('Indicator') == TARGET_INDICATOR) 
            ).drop(COLS_REMOVE)

        df_rates = df.filter(pl.col('Unit of measurement') == 'Rate per 100,000 population').rename({'VALUE': 'homicides_rate'})
        df_counts = df.filter(pl.col('Unit of measurement') == 'Counts').rename({'VALUE': 'homicides_count'})

        join_cols = ["Country", "Region", "Subregion", "Year", "Dimension", "Category", "Sex", "Age"]

        df = (
            df_rates.join(
                df_counts.select(join_cols + ['homicides_count']), # Solo traemos la columna de valor y las llaves
                on=join_cols, 
                how='inner' # Inner para asegurar que tenemos ambos datos
            ).drop("Unit of measurement")
        ).with_columns( # CÁLCULO DE POBLACIÓN
                # Evitamos división por cero. Si la tasa es 0, no podemos calcular población así.
                # En esos casos (raros en totales nacionales), la población quedará nula.
                population = pl.when(pl.col('homicides_rate') > 0)
                            .then((pl.col('homicides_count') * 100000) / pl.col('homicides_rate'))
                            .otherwise(None)
                            .round(0).cast(pl.Int64) # Población entera
        ).with_columns(
            pl.col('homicides_rate').round(2)
        ).with_columns(
                pl.when(pl.col("Country") == "Spain")
                .then(pl.lit("Spain"))   
                .when(pl.col("Country") == "United States of America") 
                .then(pl.lit("USA"))      
                .otherwise(pl.col("Region"))  
                .alias("Region_2")         
        ).with_columns(
                pl.col('Region_2').replace({'Americas': 'Latam'}),
                pl.col('Country').replace(
                    {
                        'United Kingdom (England and Wales)': 'United Kingdom',
                        'Venezuela (Bolivarian Republic of)': 'Venezuela',
                        'United States of America': 'USA'
                    }),
                pl.col('Category').replace({
                        'Socio-political homicide - terrorist offences': 'Terrorist homicide',

                        })
        ).sort(
            ["Country", "Dimension", "Category", "Sex", "Age", "Year"]
        ).with_columns(
            homicides_rate_abs_change = (pl.col("homicides_rate").diff().over(["Country", "Dimension", "Category", "Sex", "Age"])).round(2)
        )

        # 4. Save to CSV
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

        df.write_csv(OUTPUT_FILE)
        
        logger.info(f"✅ Success! Saved to: {OUTPUT_FILE}")
        logger.info(f"📊 Rows: {df.height}")

    except FileNotFoundError:
        logger.error(f"❌ Input file not found at: {INPUT_FILE}")
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    main()