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
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import polars as pl
import math
import numpy as np 

def barplot(
    df, x, y, 
    # --- Datos y Facets ---
    facet_col=None,          
    cols_wrap=2,             
    orientation='h', 
    color=None, 
    
    # --- Configuración Visual ---
    barmode='group', 
    color_discrete_map=None, 
    hover_data=None, 
    labels=None, 
    hovertemplate=None, 
    title=None,
    
    # --- Colores Eje Y (HTML) ---
    yticks_color_column=None,     
    yticks_color_map=None,  
    
    # --- Control de Orden ---
    reverse_y_order=False,   
    
    # --- Output ---
    plot_save_path=None, 
    show=None, 
    height=800,
    
    # --- Estilos y Tamaños ---
    title_size=20, 
    x_ticks_size=12, x_title_size=14, 
    y_ticks_size=12, y_title_size=14, 
    legend_size=13, legend_title_size=15,
    
    # --- Espaciado ---
    horizontal_spacing=0.15,
    vertical_spacing=0.1
    ):

    # 1. Configuración base del Layout
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
        height=height,
        barmode=barmode 
    )
    
    sort_descending = True if reverse_y_order else False

    # =========================================================================
    # RAMA A: GRÁFICO SIMPLE (SIN FACETS)
    # =========================================================================
    if not facet_col:
        tick_vals, tick_text = None, None
        
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
            # Si no hay colores, ordenamos por la métrica
            order_df = df.group_by(y).agg(pl.col(x).sum().alias('sum_x')).sort('sum_x', descending=sort_descending)
            tick_vals = order_df[y].to_list()
            df_sorted = df 

        cat_orders = {y: tick_vals} if tick_vals else None

        fig = px.bar(
            df_sorted, x=x, y=y, orientation=orientation, color=color,
            barmode=barmode, title=title, hover_data=hover_data,
            color_discrete_map=color_discrete_map,
            labels=labels,
            category_orders=cat_orders 
        )
        
        y_axis_config = dict(
            tickfont=dict(size=y_ticks_size),
            title_font=dict(size=y_title_size),
            automargin=True
        )
        
        if tick_vals:
            y_axis_config.update(dict(
                tickmode='array', 
                tickvals=tick_vals, 
                ticktext=tick_text if tick_text else tick_vals,
                type='category'
            ))
            
        fig.update_yaxes(**y_axis_config)
        fig.update_xaxes(
            tickfont=dict(size=x_ticks_size),       
            title_font=dict(size=x_title_size),     
            showgrid=True, gridcolor='#f0f0f0'
        )

    # =========================================================================
    # RAMA B: GRÁFICO CON FACETS (GRID)
    # =========================================================================
    else:
        facet_vals = df[facet_col].unique().to_list()
        facet_vals.sort() 
        
        num_plots = len(facet_vals)
        num_rows = int(np.ceil(num_plots / cols_wrap))
        
        fig = make_subplots(
            rows=num_rows, cols=cols_wrap, 
            subplot_titles=facet_vals,
            shared_xaxes=True,    
            shared_yaxes=False,   
            horizontal_spacing=horizontal_spacing,
            vertical_spacing=vertical_spacing
        )

        seen_legends = set()

        for i, val in enumerate(facet_vals):
            row = (i // cols_wrap) + 1
            col = (i % cols_wrap) + 1
            
            sub_df = df.filter(pl.col(facet_col) == val)
            
            # Blindaje duplicados (Vital para evitar barras apiladas fantasmas)
            unique_keys = [y]
            if color: unique_keys.append(color)
            sub_df = sub_df.unique(subset=unique_keys, keep='first')

            # 1. RANKING (Eje Y)
            stats_df = (
                sub_df.group_by(y)
                .agg(pl.col(x).sum().alias("total_metric"))
                .sort("total_metric", descending=sort_descending)
            )
            current_tick_vals = stats_df[y].to_list()
            current_tick_text = None

            # 2. GENERACIÓN DE TEXTO HTML
            if yticks_color_column and yticks_color_map:
                # --- CORRECCIÓN ERROR POLARS (DuplicateError) ---
                # Usamos un set o lista condicional para evitar duplicados en el select
                cols_to_select = [y]
                if yticks_color_column != y:
                    cols_to_select.append(yticks_color_column)
                
                region_map = sub_df.select(cols_to_select).unique(subset=[y], keep='first')
                stats_df = stats_df.join(region_map, on=y, how='left')
                
                try:
                    current_tick_text = [
                        f"<span style='color:{yticks_color_map[r]}; font-weight:bold'>{c}</span>"
                        for c, r in zip(stats_df[y], stats_df[yticks_color_column])
                    ]
                except:
                    current_tick_text = current_tick_vals

            # 3. ORDEN COLOR Y DATOS
            current_cat_orders = {y: current_tick_vals}
            if color:
                color_vals = sub_df[color].unique().sort().to_list()
                current_cat_orders[color] = color_vals 

            sort_cols = [y]
            if color: sort_cols.append(color)
            sub_df_sorted = sub_df.sort(sort_cols)

            # 4. GENERAR TRAZAS
            aux_fig = px.bar(
                sub_df_sorted, x=x, y=y, orientation=orientation, color=color,
                color_discrete_map=color_discrete_map,
                hover_data=hover_data, labels=labels,
                barmode=barmode,
                category_orders=current_cat_orders 
            )
            
            for trace in aux_fig.data:
                trace_name = trace.name 
                
                # --- CORRECCIÓN VISUAL: OFFSETGROUP ---
                # Esto obliga a Plotly a agrupar por color y no por índice relativo.
                # Soluciona las barras partidas en el primer subplot.
                if barmode == 'group':
                    trace.offsetgroup = trace_name
                
                if trace_name not in seen_legends:
                    trace.showlegend = True
                    seen_legends.add(trace_name)
                    trace.legendgroup = trace_name # Vincula la leyenda entre subplots
                else:
                    trace.showlegend = False
                    trace.legendgroup = trace_name
                
                fig.add_trace(trace, row=row, col=col)
            
            # 5. CONFIGURAR EJES
            y_update_args = dict(
                row=row, col=col,
                showgrid=False,
                tickfont=dict(size=y_ticks_size),
                title_font=dict(size=y_title_size),
                title_text=labels.get(y, y) if labels else y, 
                automargin=True
            )
            
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
            
            show_x_title = (row == num_rows)
            fig.update_xaxes(
                title_text=labels.get(x, x) if labels and show_x_title else (x if show_x_title else None),
                row=row, col=col, 
                showgrid=True, gridcolor='#f0f0f0',
                tickfont=dict(size=x_ticks_size),
                title_font=dict(size=x_title_size)
            )

    # =========================================================================
    # AJUSTES FINALES
    # =========================================================================
    fig.update_traces(hovertemplate=hovertemplate)
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    
    fig.update_layout(**layout_args)

    if plot_save_path:
        fig.write_html(plot_save_path, include_plotlyjs='cdn', full_html=True)
    
    if show:
        fig.show()