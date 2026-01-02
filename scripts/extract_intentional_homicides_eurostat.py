import os
import logging
import eurostat
import polars as pl

# --- LOGGING CONFIGURATION ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- PATHS & CONSTANTS ---
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_PATH = os.path.join(SCRIPT_PATH, '..')
OUTPUT_DIR = os.path.join(PROJECT_PATH, 'data', 'raw')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'eurostat_intentional_homicide_rate.csv')

DATASET_CODE = 'crim_off_cat'
TARGET_ICCS = 'ICCS0101'  # Intentional Homicide
TARGET_UNIT = 'P_HTHAB'   # Per 100,000 inhabitants

def main():
    try:
        logger.info(f"Starting extraction for dataset: {DATASET_CODE}")

        # 1. Fetch data from Eurostat API (Returns a Pandas DataFrame or list)
        data = eurostat.get_data_df(DATASET_CODE)
        
        # 2. Convert to Polars DataFrame for performance
        # Using from_pandas is safer if eurostat returns a pandas object
        df = pl.from_pandas(data)

        # 3. Filter data (Surgical extraction)
        df_filtered = df.filter(
            (pl.col('iccs') == TARGET_ICCS) & 
            (pl.col('unit') == TARGET_UNIT)
        )

        # 4. Ensure output directory exists
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            logger.info(f"Created directory: {OUTPUT_DIR}")

        # 5. Save to CSV
        df_filtered.write_csv(OUTPUT_FILE)
        logger.info(f"✅ Success. Data saved to: {OUTPUT_FILE} (Rows: {df_filtered.height})")

    except Exception as e:
        logger.error(f"Extraction failed: {e}")

if __name__ == "__main__":
    main()