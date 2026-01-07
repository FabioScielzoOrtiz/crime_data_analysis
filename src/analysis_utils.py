import polars as pl 
import numpy as np 

######################################################################################################################

def get_countries_with_enough_data(df, countries, period, prop_years_in_period_limit, by=None):
    """
    Filtra países asegurando que, si hay segmentación (by='Sex'), 
    TODOS los segmentos cumplan con el límite de datos.
    """
    start_year, end_year = period
    total_years_needed = end_year - start_year + 1
    
    # 1. Filtramos primero el DF global al periodo de interés y a los países de la lista
    # (Esto es mucho más rápido que iterar uno por uno)
    df_period = df.filter(
        (pl.col('Country').is_in(countries)) &
        (pl.col('Year') >= start_year) & 
        (pl.col('Year') <= end_year)
    )

    # 2. Definimos las claves de agrupación
    group_keys = ['Country']
    if by:
        group_keys.append(by)

    # 3. Calculamos la proporción REAL de años para cada segmento
    # Contamos años únicos presentes (n_unique) en lugar de inferir rangos
    coverage_df = (
        df_period
        .group_by(group_keys)
        .agg([
            pl.col('Year').n_unique().alias('years_count')
        ])
        .with_columns(
            (pl.col('years_count') / total_years_needed).alias('prop')
        )
    )

    # 4. Agregamos a nivel de País penalizando el peor segmento
    # Si by='Sex', un país tendrá dos filas (F y M). 
    # Tomamos el MIN de la proporción. Si M tiene 0.1 y F tiene 0.9, el país recibe 0.1.
    country_scores = (
        coverage_df
        .group_by('Country')
        .agg(
            pl.col('prop').min().alias('final_prop')
        )
    )

    # 5. Generamos el diccionario de proporciones para todos los países procesados
    # Usamos un dict comprehension de Polars para velocidad
    scores_dict = dict(zip(
        country_scores['Country'].to_list(), 
        country_scores['final_prop'].round(2).to_list()
    ))
    
    # Rellenamos países que no tenían ningún dato en el periodo (prop = 0)
    for c in countries:
        if c not in scores_dict:
            scores_dict[c] = 0.0

    # 6. Filtramos la lista final
    countries_with_enough_data = [
        c for c, p in scores_dict.items() 
        if p >= prop_years_in_period_limit
    ]
    
    # Ordenamos la lista para consistencia
    countries_with_enough_data.sort()

    return countries_with_enough_data, scores_dict

######################################################################################################################

def process_time_series_data(
    df, 
    selected_countries, 
    prop_years_in_period_limit, 
    ref_region_for_start_year='Europe',
    by=None,             # 'Sex', 'Age', 'Category' o None
    age_mapping=None,     # Solo requerido si by='Age'
    dimension=None
):
    """
    Genera DataFrames de series temporales filtrando dinámicamente por:
    - Total
    - Sexo (Dimension=Total, Sex!=Total)
    - Edad (Dimension=Total, Age!=Total + Mapeo)
    - Contexto (Dimension='by situational context', Category!=Total)
    """
    
    df_time_series = {}

    # -------------------------------------------------------------------------
    # 1. FILTRADO INICIAL Y LÓGICA CONDICIONAL
    # -------------------------------------------------------------------------
    
    # Filtro común para todos los casos: Solo los países seleccionados
    country_filter = pl.col('Country').is_in(selected_countries)
    
    init_msg = f"⚙️ Procesando desglose por: {by.upper()}" if by else f"⚙️ Procesando desglose por: TOTAL PAÍS"
    print(init_msg)
    print('-'*80)
    
    if by == 'Category':
        # --- NUEVO CASO: SITUATIONAL CONTEXT ---
       
        df_country = df.filter(
            country_filter &
            (pl.col('Dimension') == dimension) & # Dimensión específica
            (pl.col('Category') != 'Total') &    # Queremos las subcategorías
            (pl.col('Sex') == 'Total') &
            (pl.col('Age') == 'Total')
        )


    elif by == 'Sex':
        # --- CASO SEXO ---

        df_country = df.filter(
            country_filter &
            (pl.col('Dimension') == 'Total') &
            (pl.col('Category') == 'Total') &
            (pl.col('Sex') != 'Total') &      # Male / Female
            (pl.col('Age') == 'Total')
        )

    elif by == 'Age':
        # --- CASO EDAD ---

        # A. Pre-filtro y Mapeo
        
        df_pre = df.clone()

        if age_mapping:
            
            df_pre = df_pre.with_columns(
                pl.col('Age').replace(age_mapping) 
            )
        
        df_pre = df_pre.filter(
            country_filter &
            (pl.col('Dimension') == 'Total') &
            (pl.col('Category') == 'Total') &
            (pl.col('Age') != 'Total')        # Grupos de edad
        )

        # B. Agregación (Suma de conteos / Recálculo de tasas por el reagrupamiento)
        has_counts = 'homicides_count' in df.columns
        has_pop = 'population' in df.columns
        
        # Columnas de agrupación (Aseguramos mantener Region_2)
        grp_cols = ['Country', 'Region_2', 'Year', 'Age']
        
        agg_expr = (
            (pl.col('homicides_count').sum() / pl.col('population').sum() * 100000).round(2)
            if (has_counts and has_pop)
            else pl.mean('homicides_rate').round(2)
        )
        
        # Agregamos conteos y poblaciones si existen para no perderlos
        agg_list = [agg_expr.alias('homicides_rate')]
        if has_counts: agg_list.append(pl.col('homicides_count').sum())
        if has_pop:    agg_list.append(pl.col('population').sum())

        df_country = df_pre.group_by(grp_cols).agg(agg_list)
        
        # RECALCULAR LA DIFERENCIA ABSOLUTA
        df_country = (
            df_country
            .sort(['Country', 'Age', 'Year']) # Orden vital para series temporales
            .with_columns(
                homicides_rate_abs_change = pl.col('homicides_rate')
                                            .diff()
                                            .over(['Country', 'Age']) # Diff por País y Grupo de Edad
                                            .round(2)
            )
        )

    else:
        # --- CASO TOTAL (Headline Rate) ---

        df_country = df.filter(
            country_filter &
            (pl.col('Dimension') == 'Total') &
            (pl.col('Category') == 'Total') &
            (pl.col('Sex') == 'Total') &
            (pl.col('Age') == 'Total')
        )
    

    countries_with_data = df_country['Country'].unique().to_list()
    countries_without_data = [c for c in selected_countries if c not in countries_with_data]
    print(f'📊 Paises SIN datos de este tipo:')
    print(f'   - Número: {len(countries_without_data)} de {len(selected_countries)}')
    print(f'   - Lista: {countries_without_data}')
    print('-'*80)

    # Ordenamiento final (Vital para visualización)
    df_time_series['country'] = df_country.sort(["Country", "Year"])
    

    # -------------------------------------------------------------------------
    # 2. DEFINICIÓN DEL PERIODO (Automático basado en Región ref)
    # -------------------------------------------------------------------------
    try:
        # Intentamos usar el Q25 de Europa para fijar el año inicial
        europe_years = df_time_series['country'].filter(pl.col('Region_2') == ref_region_for_start_year)['Year']
        if not europe_years.is_empty():
            min_year = int(europe_years.quantile(0.25))
        else:
            min_year = df_time_series['country']['Year'].min()
    except:
        min_year = 1990 # Fallback seguro
        
    max_year = df_time_series['country']['Year'].max()

    # -------------------------------------------------------------------------
    # 3. FILTRO DE CALIDAD (Suficiencia de datos)
    # -------------------------------------------------------------------------
    # Pasamos 'by' para que valide que existan datos para TODAS las categorías
    # (ej. si by='Category', valida que tenga datos de Gangs, Interpersonal, etc.)
    countries_with_enough_data, prop_year_in_period = get_countries_with_enough_data(
        df = df_time_series['country'], 
        countries = selected_countries,
        period = [min_year, max_year],
        prop_years_in_period_limit = prop_years_in_period_limit,
        by = by 
    )

    # -------------------------------------------------------------------------
    # 4. SERIES REGIONALES (Agregación Ponderada)
    # -------------------------------------------------------------------------
    # Agrupamos por Región, Año y la variable de desglose si existe
    group_cols_region = ['Region_2', 'Year']
    if by: group_cols_region.append(by)

    # Detectamos si podemos usar el método preciso (Conteos/Población)
    has_precision = 'homicides_count' in df_country.columns and 'population' in df_country.columns
    
    if has_precision:
        # Fórmula: (Suma Muertos / Suma Pob) * 100k
        agg_regional = (pl.col('homicides_count').sum() / pl.col('population').sum() * 100000)
    else:
        # Fallback: Promedio simple
        agg_regional = pl.mean('homicides_rate')

    df_time_series['region'] = (
        df_time_series['country']
        .filter(pl.col('Country').is_in(countries_with_enough_data))
        .group_by(group_cols_region)
        .agg(agg_regional.round(2).alias('mean_homicides_rate'))
        .sort(group_cols_region)
    )

    # Logs de control
    print(f"📅 Periodo para región: {min_year}-{max_year}")
    print(f"✅ Países válidos para región: {len(countries_with_enough_data)} de {len(selected_countries)}")
    print('-'*80)

    return df_time_series, min_year, max_year

######################################################################################################################

def calculate_ranking_country(df, countries, prop_years_in_period_limit, start_year, end_year, by=None):
    """
    Calcula el ranking de países (o segmentos país-sexo/edad) para un periodo dado.
    Si existen columnas de conteo y población, calcula la tasa ponderada del periodo.
    Si no, usa el promedio simple de las tasas anuales.
    """
    
    # 1. Mapa de regiones ligero (para pegar después)
    df_regions_map = df.select(['Country', 'Region_2']).unique()
    
    # 2. Filtrar países con suficientes datos (Usando tu función optimizada)
    ranking_selected_countries, prop_year_in_period = get_countries_with_enough_data(
        df = df, 
        countries=countries,
        period = [start_year, end_year],
        prop_years_in_period_limit = prop_years_in_period_limit,
        by=by
    )

    ranking_not_selected_countries = [c for c in countries if c not in ranking_selected_countries]

    # 3. Definir columnas de agrupación
    group_cols = ['Country']
    if by:
        group_cols.append(by)

    # 4. Lógica de Agregación (El "Nuevo Enfoque")
    # Verificamos si tenemos los datos para hacer el cálculo ponderado (más preciso)
    has_precision_data = 'homicides_count' in df.columns and 'population' in df.columns

    if has_precision_data:
        # Tasa del Periodo = (Suma Muertes Periodo / Suma Población Periodo) * 100k
        # Esto evita sesgos si la población cambió mucho en 30 años.
        agg_expr = (pl.col('homicides_count').sum() / pl.col('population').sum() * 100000)
    else:
        # Fallback: Promedio simple de tasas anuales (tu método anterior)
        agg_expr = pl.mean('homicides_rate')

    # 5. Construcción del DataFrame
    df_ranking = (
        df
        .filter(
            pl.col('Year').is_between(start_year, end_year),
            pl.col('Country').is_in(ranking_selected_countries)
        )
        .group_by(group_cols)
        .agg(
            agg_expr.round(2).alias('mean_homicides_rate')
        )
        # Unir región
        .join(
            df_regions_map, 
            on='Country', 
            how='left'
        )
        # Ordenar (Ascendente para que Plotly horizontal ponga el mayor arriba)
        .sort("mean_homicides_rate", descending=False)
    )
    
    # 6. Logs informativos
    print('-'*100)
    print(f'📊 Ranking Period: {start_year} - {end_year}')
    if by: print(f'   Segmentado por: {by}')
    print(f'   Países analizados: {len(countries)}')
    print(f'   Países seleccionados (Data > {prop_years_in_period_limit*100}%): {len(ranking_selected_countries)}')
    print(f'   Países descartados: {ranking_not_selected_countries}')
    print(f'   Prop. datos (años) en el periodo, por pais: {prop_year_in_period}')
    print('-'*100)
    
    return df_ranking

######################################################################################################################

def process_ranking_data(
    df, 
    selected_countries, 
    prop_years_in_period_limit, 
    initial_years, 
    max_year,
    by=None # <--- NUEVO ARGUMENTO NECESARIO
):
    """
    Orquestador para generar rankings combinados.
    Ahora soporta agrupación dinámica ('by') para regiones.
    """

    df_ranking_dict = {'country': {}, 'region': {}}
    combined_list_country = []
    combined_list_region = []

    # Columnas para agrupar la región
    # Si by='Sex', agrupamos por ['Region_2', 'Sex']
    region_group_cols = ['Region_2']
    if by:
        region_group_cols.append(by)

    for initial_year in initial_years:

        print(f"🔄 Procesando ranking ({by if by else 'Total'}) para: {initial_year}-{max_year}")
        
        # A. Ranking País
        df_rank = calculate_ranking_country(
            df = df, 
            countries = selected_countries, 
            prop_years_in_period_limit = prop_years_in_period_limit, 
            start_year = initial_year, 
            end_year = max_year,
            by = by # <--- Pasamos el argumento
        )
        
        df_ranking_dict['country'][initial_year] = df_rank
        
        label_period = f"{initial_year}-{max_year}"
        combined_list_country.append(
            df_rank.with_columns(pl.lit(label_period).alias("Periodo"))
        )

        # B. Ranking Región (ADAPTADO)
        # Agregamos usando las columnas dinámicas
        df_region_rank = (
            df_rank
            .group_by(region_group_cols) # <--- USO DE GRUPO DINÁMICO
            .agg(pl.mean('mean_homicides_rate').round(2))
            .sort('mean_homicides_rate', descending=False)
        )
        
        df_ranking_dict['region'][initial_year] = df_region_rank
        
        combined_list_region.append(
            df_region_rank.with_columns(pl.lit(label_period).alias("Periodo"))
        )

    # Concatenación Final
    df_ranking_combined = {
        'country': pl.concat(combined_list_country) if combined_list_country else None,
        'region': pl.concat(combined_list_region) if combined_list_region else None
    }
    
    print("✅ Rankings procesados y combinados correctamente.")
    
    return df_ranking_combined, df_ranking_dict

######################################################################################################################