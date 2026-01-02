#################################################################################################################

SELECTED_COUNTRIES = {}

SELECTED_COUNTRIES['world'] = [
    # --- EL PROTAGONISTA ---
    'Spain',

    # --- VECINOS Y PARES EUROPEOS (El estándar) ---
    'Portugal',
    'France',
    'Italy',
    'Germany',
    'United Kingdom', # Ojo: En tu lista el UK está dividido
    'Sweden',   # Importante por el debate actual sobre bandas
    'Norway',
    'Denmark',
    'Romania',  # Importante: gran comunidad en España

    # --- LATINOAMÉRICA (Vínculo cultural + Alta criminalidad) ---
    'Brazil',
    'Mexico',
    'Colombia',
    'Venezuela',
    'Argentina',
    'El Salvador', # Interesante por su cambio drástico reciente
    'Chile',

    # --- ÁFRICA (Vínculo migratorio) ---
    'Morocco',  # CRÍTICO: Principal origen de inmigración en España
    'South Africa', # Referencia de alta criminalidad global

    # --- POTENCIAS GLOBALES / REFERENCIAS ---
    'USA', # El gran comparador occidental
    'Japan',    # El estándar de seguridad máxima
    'China'
]

SELECTED_COUNTRIES['europe'] = [
    'Spain',
    'Portugal',
    'France',
    'Italy',
    'Germany',
    'United Kingdom',  
    'Sweden',   
    'Norway',
    'Denmark',
    'Romania'
]

SELECTED_COUNTRIES['latam'] = [
    'Spain',
    'Brazil',
    'Mexico',
    'Colombia',
    'Venezuela',
    'Argentina',
    'El Salvador', 
    'Chile',
]

SELECTED_COUNTRIES['usa'] = [
    'Spain',
    'USA'
]

#################################################################################################################

COLOR_MAP = {}

COLOR_MAP['world'] = {
    "Spain": "#FF0000",  # Rojo brillante
    "USA": "#ED53AF",
    "Europe": "#1f77b4",     # Azul
    "Latam": "#2ca02c",   # Verde
    "Asia": "#ff7f0e",       # Naranja
    "Africa": "#9467bd",     # Morado
}

COLOR_MAP['europe'] = {}

COLOR_MAP['latam'] = {}

COLOR_MAP['usa'] = {}

#################################################################################################################

CATEGORY_ORDERS = {} 

CATEGORY_ORDERS['world'] = {
    "Region_2": ["Spain", "USA", "Europe", "Latam", "Africa", "Asia"]
}

CATEGORY_ORDERS['europe'] = {}

CATEGORY_ORDERS['latam'] = {}

CATEGORY_ORDERS['usa'] = {}

#################################################################################################################

PLOT_FILENAME = {}

PLOT_FILENAME[('world', 'time_series')] = 'time_series_total_homicides_world.html'

PLOT_FILENAME[('world', 'ranking')] = 'mean_homicides_world.html'

PLOT_FILENAME[('europe', 'time_series')] = ''

PLOT_FILENAME[('latam', 'time_series')] = ''

PLOT_FILENAME[('usa', 'time_series')] = ''

#################################################################################################################

HOVER_DATA = {} 

HOVER_DATA['time_series'] = {
    "Region": True,       # Mostrar Región
    "Subregion": True,    # Mostrar Subregión
    "Year": True,         # Mostrar Año
    "homicides_rate": True, # Mostrar Tasa
    "Region_2": False, # <--- ¡ESTO OCULTA LA LEYENDA/COLOR!
    "Country": True      # Ocultar del cuerpo (ya sale en el título)
}

HOVER_DATA['ranking'] = {'Country': False}

#################################################################################################################

LABELS = {}

LABELS['time_series'] = {
    "homicides_rate": "Tasa (por 100k hab.)",
    "Year": "Año",
    "Country": "País",
    "Region_2": "Región"
}

LABELS['ranking'] = {
    "homicides_rate": "Tasa de Homicidios",
    "Country": "País"        
}

#################################################################################################################

PROP_YEARS_IN_PERIOD_LIMIT = 0.80

#################################################################################################################