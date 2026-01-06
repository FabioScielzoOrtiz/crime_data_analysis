import plotly.express as px
from plotly.subplots import make_subplots
import polars as pl
import numpy as np  

#################################################################################################################

def time_series_plot(
        df, x, y, height=600, title=None, line_group=None, color=None, 
        line_dash=None, facet_col=None, facet_row=None,  facet_col_wrap=None,    
        color_discrete_map=None, category_orders=None, 
        hover_name=None, hover_data=None, labels=None, 
        hovertemplate=None, title_size=20, x_ticks_size=14, x_title_size=16, 
        y_ticks_size=14, y_title_size=16, legend_size=14, legend_title_size=16,
        plot_save_path=None, show=True,
        default_visible_name=None 
    ):

    # Crear el gráfico de líneas
    fig = px.line(
        df, x=x, y=y, color=color, line_group=line_group,
        line_dash=line_dash, facet_col=facet_col, 
        facet_row=facet_row, facet_col_wrap=facet_col_wrap,
        hover_name=hover_name, title=title, hover_data=hover_data, 
        markers=True, category_orders=category_orders, 
        color_discrete_map=color_discrete_map, labels=labels
    )

    fig.update_traces(hovertemplate=hovertemplate)

    # --- CAMBIO CLAVE: APLICAR ESTILOS A TODOS LOS EJES ---
    # Usamos update_xaxes y update_yaxes para asegurar que la config 
    # se aplique a TODOS los subplots (izquierda y derecha)
    
    fig.update_xaxes(
        showgrid=False,
        tickfont=dict(size=x_ticks_size), 
        title_font=dict(size=x_title_size)
    )

    fig.update_yaxes(
        showgrid=True,             # <--- Esto ahora activará la grid en AMBOS lados
        gridcolor='lightgray',
        tickfont=dict(size=y_ticks_size), 
        title_font=dict(size=y_title_size)
    )
    # ------------------------------------------------------

    # Lógica de ejes independientes (facet)
    if facet_col or facet_row:
        fig.update_yaxes(matches=None) 
        fig.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True))

    # Lógica de visibilidad por defecto
    if default_visible_name:
            # 1. Si el usuario pasa un solo string ("Spain"), lo convertimos a lista ["Spain"]
            #    Si ya es una lista, la dejamos tal cual.
            names_to_show = [default_visible_name] if isinstance(default_visible_name, str) else default_visible_name
            
            # 2. Verificamos si el nombre de la traza NO está en esa lista
            fig.for_each_trace(lambda trace: trace.update(visible="legendonly") 
                            if trace.name not in names_to_show else None)

    # Layout general (Fondo, Título, Leyenda)
    fig.update_layout(
        plot_bgcolor='white', 
        height=height,  
        title=dict(text=f"<b>{title}</b>" if title else None, font=dict(size=title_size), x=0.5, xanchor='center'),
        legend=dict(font=dict(size=legend_size), title_font=dict(size=legend_title_size))
    )
    
    # Limpiar títulos de los facets
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    
    if plot_save_path:
        fig.write_html(plot_save_path, include_plotlyjs='cdn', full_html=True)
    
    if show:
        fig.show()

#################################################################################################################

def barplot(
    df, x, y, 
    # --- Datos y Facets ---
    facet_col=None,          # Columna para dividir (ej. 'Periodo', 'Sex')
    cols_wrap=2,             # Columnas en el grid (si hay facet)
    orientation='h', 
    color=None, 
    
    # --- Configuración Visual ---
    barmode=None,
    color_discrete_map=None, 
    hover_data=None, 
    labels=None, 
    hovertemplate=None, 
    title=None,
    
    # --- Colores Eje Y (HTML) ---
    yticks_color_column=None,     
    yticks_color_map=None,  
    
    # --- Control de Orden ---
    reverse_y_order=False,   # False = Mayor arriba (Top), True = Menor arriba
    
    # --- Output ---
    plot_save_path=None, 
    show=None, 
    height=800,
    
    # --- Estilos y Tamaños ---
    title_size=20, 
    x_ticks_size=12, x_title_size=14, 
    y_ticks_size=12, y_title_size=14, 
    legend_size=13, legend_title_size=15,
    
    # --- Espaciado (Solo para facets) ---
    horizontal_spacing=0.15,
    vertical_spacing=0.1
    ):

    # 1. Configuración base del Layout (Común para todos)
    layout_args = dict(
        plot_bgcolor='white',      
        title=dict(
            text=f"<b>{title}</b>" if title else None, 
            font=dict(size=title_size), x=0.5, xanchor='center'
        ),
        legend=dict(
            font=dict(size=legend_size), 
            title_font=dict(size=legend_title_size)
        ),
        height=height
    )
    
    # Definir dirección de ordenamiento (Plotly dibuja de abajo a arriba)
    # descending=False -> [1, 10, 100] -> 100 queda arriba.
    sort_descending = True if reverse_y_order else False

    # =========================================================================
    # RAMA A: GRÁFICO SIMPLE (SIN FACETS)
    # =========================================================================
    if not facet_col:
        tick_vals, tick_text = None, None
        
        # A.1. Calcular orden global y Textos HTML (si aplica)
        if yticks_color_column and yticks_color_map:
            stats_df = (
                df.group_by(y)
                .agg([
                    pl.col(x).sum().alias("total_metric"),       
                    pl.col(yticks_color_column).first().alias("region_name") 
                ])
                .sort("total_metric", descending=sort_descending) 
            )
            ordered_items = stats_df[y].to_list()
            ordered_regions = stats_df["region_name"].to_list()
            
            # Ordenar el DF original para alinear la visualización
            df_sorted = df.sort(x, descending=sort_descending)
            
            try:
                tick_text = [
                    f"<span style='color:{yticks_color_map[r]}; font-weight:bold'>{c}</span>"
                    for c, r in zip(ordered_items, ordered_regions)
                ]
                tick_vals = ordered_items
            except KeyError:
                tick_vals = ordered_items
                tick_text = ordered_items

        else:
            # Si no hay colores especiales, solo ordenamos por la métrica
            df_sorted = df.sort(x, descending=sort_descending)
            ordered_items = None
            tick_vals = None

        # A.2. Crear Gráfico Simple
        fig = px.bar(
            df_sorted, x=x, y=y, orientation=orientation, color=color,
            barmode=barmode, title=title, hover_data=hover_data,
            color_discrete_map=color_discrete_map,
            labels=labels
        )
        
        # A.3. Estilos Eje Y
        y_axis_config = dict(
            tickfont=dict(size=y_ticks_size),
            title_font=dict(size=y_title_size),
            automargin=True
        )
        
        if tick_vals:
            y_axis_config.update(dict(
                tickmode='array', 
                tickvals=tick_vals, 
                ticktext=tick_text,
                type='category',
                categoryorder='array',
                categoryarray=tick_vals
            ))
            
        fig.update_yaxes(**y_axis_config)

        # A.4. Estilos Eje X
        fig.update_xaxes(
            tickfont=dict(size=x_ticks_size),       
            title_font=dict(size=x_title_size),     
            showgrid=True, gridcolor='#f0f0f0'
        )

    # =========================================================================
    # RAMA B: GRÁFICO CON FACETS (GRID COMPARATIVO O INDEPENDIENTE)
    # =========================================================================
    else:
        # B.1. Preparar Grid
        facet_vals = df[facet_col].unique().to_list()
        facet_vals.sort() # Ordenar facets (ej. cronológicamente o alfabéticamente)
        
        num_plots = len(facet_vals)
        num_rows = int(np.ceil(num_plots / cols_wrap))
        
        # B.2. Crear Figura con Subplots
        fig = make_subplots(
            rows=num_rows, cols=cols_wrap, 
            subplot_titles=facet_vals,
            shared_xaxes=True,    # Compartir X para comparar magnitudes
            shared_yaxes=False,   # Y Independiente para respetar rankings distintos
            horizontal_spacing=horizontal_spacing,
            vertical_spacing=vertical_spacing
        )

        seen_legends = set()

        # B.3. Iterar Subplots
        for i, val in enumerate(facet_vals):
            row = (i // cols_wrap) + 1
            col = (i % cols_wrap) + 1
            
            # Filtrar datos del facet actual
            sub_df = df.filter(pl.col(facet_col) == val)
            
            # Variables locales para este subplot
            current_tick_vals = None
            current_tick_text = None
            
            # B.3.1. Calcular orden ESPECÍFICO para este facet
            if yticks_color_column and yticks_color_map:
                stats_df = (
                    sub_df.group_by(y)
                    .agg([
                        pl.col(x).sum().alias("total_metric"),       
                        pl.col(yticks_color_column).first().alias("region_name") 
                    ])
                    .sort("total_metric", descending=sort_descending)
                )
                ordered_items = stats_df[y].to_list()
                ordered_regions = stats_df["region_name"].to_list()
                
                try:
                    current_tick_text = [
                        f"<span style='color:{yticks_color_map[r]}; font-weight:bold'>{c}</span>"
                        for c, r in zip(ordered_items, ordered_regions)
                    ]
                    current_tick_vals = ordered_items
                except KeyError:
                    current_tick_vals = ordered_items
            else:
                # Si no hay config de colores, calculamos el orden basado solo en la métrica
                # Esto es necesario para tickvals si queremos forzar el orden
                temp_sort = sub_df.sort(x, descending=sort_descending)
                current_tick_vals = temp_sort[y].unique(maintain_order=True).to_list()
            
            # B.3.2. Ordenar el DF localmente (Clave para Plotly Horizontal)
            sub_df_sorted = sub_df.sort(x, descending=sort_descending)

            # B.3.3. Generar trazas auxiliares
            aux_fig = px.bar(
                sub_df_sorted, x=x, y=y, orientation=orientation, color=color,
                color_discrete_map=color_discrete_map,
                hover_data=hover_data, labels=labels
            )
            
            # B.3.4. Añadir trazas y gestionar leyenda
            for trace in aux_fig.data:
                trace_name = trace.name 
                if trace_name not in seen_legends:
                    trace.showlegend = True
                    seen_legends.add(trace_name)
                else:
                    trace.showlegend = False
                fig.add_trace(trace, row=row, col=col)
            
            # B.3.5. Actualizar Eje Y del Subplot
            y_update_args = dict(
                row=row, col=col,
                showgrid=False,
                tickfont=dict(size=y_ticks_size),
                title_font=dict(size=y_title_size),
                title_text=labels.get(y, y) if labels else y, # Forzar título Y
                automargin=True
            )
            
            # Aplicar orden forzado y colores si existen
            if current_tick_vals:
                y_update_args.update(dict(
                    tickmode='array', 
                    tickvals=current_tick_vals, 
                    ticktext=current_tick_text if current_tick_text else current_tick_vals,
                    type='category', 
                    categoryorder='array', 
                    categoryarray=current_tick_vals 
                ))
            
            fig.update_yaxes(**y_update_args)
            
            # B.3.6. Actualizar Eje X del Subplot
            # Solo mostrar título en la última fila si compartimos ejes, o siempre si es necesario
            show_x_title = (row == num_rows)
            
            fig.update_xaxes(
                title_text=labels.get(x, x) if labels and show_x_title else (x if show_x_title else None),
                row=row, col=col, 
                showgrid=True, gridcolor='#f0f0f0',
                tickfont=dict(size=x_ticks_size),
                title_font=dict(size=x_title_size)
            )

    # =========================================================================
    # AJUSTES FINALES COMUNES
    # =========================================================================
    fig.update_traces(hovertemplate=hovertemplate)
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    
    fig.update_layout(**layout_args)

    if plot_save_path:
        fig.write_html(plot_save_path, include_plotlyjs='cdn', full_html=True)
    
    if show:
        fig.show()