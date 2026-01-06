import polars as pl 
import numpy as np 

######################################################################################################################

def get_countries_with_enough_data(df, countries, period, prop_years_in_period_limit, by=None):

    prop_year_in_period = {}
    period_array = range(period[0], period[1] + 1)
    for c in countries:
        if by: 
            df_temp = df.filter(pl.col('Country') == c).group_by(by).agg(pl.min('Year').alias('min_year'), pl.max('Year').alias('max_year'))  
            max = df_temp['max_year'].min()
            min = df_temp['min_year'].max()
            if min and max:
                country_years = list(range(min, max + 1))
        else:
            country_years = df.filter(pl.col('Country') == c)['Year'].unique().to_list()
        prop_year_in_period[c] = np.round(np.mean([x in country_years for x in period_array]), 2)

    countries_with_enough_data = [c for c, p in prop_year_in_period.items() if p >= prop_years_in_period_limit]

    return countries_with_enough_data, prop_year_in_period

######################################################################################################################

def calculate_ranking_country(df_time_series, countries, prop_years_in_period_limit, start_year, end_year, by=None):

    df_regions_map = df_time_series.select(['Country', 'Region_2']).unique()
       
    ranking_selected_countries, prop_year_in_period = get_countries_with_enough_data(
        df = df_time_series, 
        by=by,
        countries=countries,
        period = [start_year, end_year],
        prop_years_in_period_limit = prop_years_in_period_limit
    )

    ranking_not_selected_countries = [c for c in countries if c not in ranking_selected_countries]

    df_ranking = df_time_series.filter(
        pl.col('Year').is_between(start_year, end_year),
        pl.col('Country').is_in(ranking_selected_countries)
        ).group_by(
            ['Country', by] if by else 'Country'
        ).agg(
            pl.mean('homicides_rate').round(2).alias('mean_homicides_rate')
        ).join(
            df_regions_map, 
            on='Country', 
            how='left'
        ).unique().sort(
            "mean_homicides_rate", 
            descending=False
        ) 
    
    print('ranking_period:', start_year, '-', end_year)
    print('ranking_selected_countries:', ranking_selected_countries)
    print('ranking_not_selected_countries:', ranking_not_selected_countries)
    print('prop_year_in_period:', prop_year_in_period)
    print('-'*150)
    
    return df_ranking

######################################################################################################################