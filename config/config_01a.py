#################################################################################################################

SELECTED_COUNTRIES = [
    # --- EL PROTAGONISTA ---
    'Spain',

    # --- VECINOS Y PARES EUROPEOS (El estándar) ---
    'Portugal',
    'France',
    'Italy',
    'Germany',
    'United Kingdom', 
    'Sweden',   # Crisis de bandas actual
    'Norway',
    'Denmark',
    'Romania',  # Importante comunidad en España
    'Greece',   # Referente mediterráneo (Tu adición)

    # --- LATINOAMÉRICA (Vínculo cultural + Alta violencia) ---
    'Brazil',
    'Mexico',
    'Colombia',
    'Venezuela',
    'Argentina',
    'El Salvador', # El efecto Bukele (Caída drástica)
    'Chile',

    # --- ASIA / PACÍFICO (Modelos de seguridad y contrastes) ---
    'Japan',        # Estándar de seguridad #1
    'Republic of Korea',  # Estándar de seguridad #2 (NUEVO)
    'Singapore',    # Ciudad-estado autoritaria/segura (Tu adición)
    'China',
    'India',
    'Philippines',  # Nexo hispano
    'Indonesia',    # Gigante demográfico musulmán (NUEVO)
    'Thailand',     # Referente turístico regional (NUEVO)
    'Türkiye',       # IMPORTANTE: UNODC suele usar 'Turkey', no 'Türkiye'

    # --- ÁFRICA (Vecindad y demografía) ---
    'Morocco',      # Vecino frontera sur
    'Egypt',        # Gigante del norte de África / Turismo (NUEVO)
    'South Africa', # Outlier de violencia extrema
    
    # --- POTENCIA GLOBAL ---
    'USA'           # El gran comparador occidental
]

#################################################################################################################

COLOR_MAP = {}

COLOR_MAP['Region_2'] = {
    "Spain": "#FF0000",  # Rojo brillante
    "USA": "#13020D",
    "Europe": "#0883db",     # Azul
    "Latam": "#2ca02c",   # Verde
    "Asia": "#ff7f0e",       # Naranja
    "Africa": "#a02ff1",     # Morado
}

COLOR_MAP['Sex'] = {
    "Male": "#62CBDE",   
    "Female": "#EFA0E8"
}

#################################################################################################################

CATEGORY_ORDERS = {
    "Region_2": ["Spain", "USA", "Europe", "Latam", "Africa", "Asia"],
    "Sex": ["Female", "Male",]
}

#################################################################################################################

HOVER_DATA = {} 

HOVER_DATA['time_series_country'] = {
    "Region": False,    
    "Region_2": False,    
    "Subregion": False,    
    "Country": True ,     
    "Year": True,        
    "homicides_rate": True, 
    "homicides_rate_abs_change": True
}

HOVER_DATA['time_series_region'] = {
    "Region_2": False,    
    "Year": True,        
    "mean_homicides_rate": True, 
}

HOVER_DATA['ranking_country'] = {
    'Country': True, 
    "Region_2": True,
    "mean_homicides_rate": True
    }

HOVER_DATA['ranking_region'] = {
    "Region_2": True,
    "mean_homicides_rate": True
    }

#################################################################################################################

LABELS = {}

LABELS['time_series'] = {
    "homicides_rate": "Tasa de Homicidios",
    "Year": "Año",
    "Country": "País",
    "Region_2": "Región",
    "homicides_rate_abs_change": "Variación Absoluta"
}

LABELS['ranking'] = {
    "mean_homicides_rate": "Tasa Media de Homicidios",
    "Country": "País" ,
    "Region_2": "Región"      
}

#################################################################################################################

HOVER_TEMPLATES = {}

HOVER_TEMPLATES['time_series_country'] = (
        "<b style='font-size: 14px'>%{customdata[3]}</b><br>" 
        "<br>" 
        
        # Línea 1: AÑO
        "<b>Año:</b> %{x}<br>"
        
        # Línea 2: TASA (Usando tu etiqueta exacta y formato .2f)
        "<b>Tasa de Homicidios:</b> %{y:.2f}<br>"
        
        # Línea 3: VARIACIÓN (Usando tu etiqueta exacta y formato +.2f)
        "<b>Variación Absoluta:</b> %{customdata[4]:+.2f}"
        
        # Ocultamos la etiqueta secundaria de la derecha
        "<extra></extra>"
    )

HOVER_TEMPLATES['time_series_region'] = (
        # Título: Region (en grande y negrita)
        "<b style='font-size: 14px'>%{customdata[0]}</b><br>" 
        "<br>" 
        
        # Línea 1: AÑO
        "<b>Año:</b> %{x}<br>"
        
        # Línea 2: TASA (Usando tu etiqueta exacta y formato .2f)
        "<b>Tasa Media de Homicidios:</b> %{y:.2f}<br>"
        
        # Ocultamos la etiqueta secundaria de la derecha
        "<extra></extra>"
    )

HOVER_TEMPLATES['ranking_country'] = (
        "<b style='font-size: 14px'>%{y}</b><br>" 
        "<br>" 
        
        "<b>Región:</b> %{customdata[0]}<br>"
        "<b>Tasa Media de Homicidios:</b> %{x:.2f}<br>"
        
        "<extra></extra>"
    )

HOVER_TEMPLATES['ranking_region'] = (
        "<b style='font-size: 14px'>%{y}</b><br>" 
        "<br>" 
        
        "<b>Tasa Media de Homicidios:</b> %{x:.2f}<br>"
        
        "<extra></extra>"
    )

#################################################################################################################

PROP_YEARS_IN_PERIOD_LIMIT = 0.65

#################################################################################################################

PLOT_FILENAME = {}

PLOT_FILENAME['time_series'] = 'time_series_total_homicides_world.html'

PLOT_FILENAME['ranking_country'] = f'mean_homicides_world_by_country.html'

PLOT_FILENAME['ranking_region'] = f'mean_homicides_world_by_region.html'

#################################################################################################################