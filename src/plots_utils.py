import plotly.express as px
from plotly.subplots import make_subplots
import polars as pl

#################################################################################################################

def time_series_plot(
        df, x, y, height=600, title=None, line_group=None, color=None, 
        line_dash=None, facet_col=None, facet_row=None,      
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
        line_dash=line_dash, facet_col=facet_col, facet_row=facet_row,
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

def barplot_01a(
    df, x, y, height=600, orientation=None, color=None, 
    color_discrete_map=None, hover_data=None, 
    labels=None, hovertemplate=None, 
    category_orders=None, title=None,
    title_size=20, x_ticks_size=14, x_title_size=16, 
    y_ticks_size=14, y_title_size=16, 
    legend_size=14, legend_title_size=16,
    plot_save_path=None, show=None
    ):

    fig = px.bar(
        df,
        x=x,
        y=y,
        orientation=orientation,       # Barras Horizontales
        color=color,   
        title=title,
        hover_data=hover_data,
        category_orders=category_orders, 
        color_discrete_map=color_discrete_map,
        labels=labels
    )

    fig.update_traces(
        hovertemplate=hovertemplate
    )

    fig.update_layout(
        plot_bgcolor='white',      # Fondo limpio
        showlegend=True,          
        height=height,                # Altura ajustada a la cantidad de países
        xaxis=dict(
            showgrid=True, 
            gridcolor='#f0f0f0',
            #side='top',           
            tickfont=dict(size=x_ticks_size), 
            title_font=dict(size=x_title_size)
        ),
        yaxis=dict(
            showgrid=False,
            categoryorder='total ascending',
            tickfont=dict(size=y_ticks_size), 
            title_font=dict(size=y_title_size)  
        ),
        title=dict(
            text=f"<b>{title}</b>" if title else None, # Inyectamos HTML para negrita
            font=dict(size=title_size),
            x=0.5, # Opcional: Centrar título (si no te gusta, borra esta línea)
            xanchor='center'
        ),
        legend=dict(
            font=dict(size=legend_size),
            title_font=dict(size=legend_title_size) # El título de la leyenda un pelín más grande
        )
    )

    # Personalizar el texto de las barras (hacerlo negrita y legible)
    fig.update_traces(
        textfont_size=12, 
        textangle=0, 
        textposition="outside", # Poner número fuera si la barra es muy corta
        cliponaxis=False        # Permitir que el texto sobresalga del gráfico si es necesario
    )
     
    
    if plot_save_path:
        # Guardar el archivo
        fig.write_html(
            plot_save_path,
            include_plotlyjs='cdn', 
            full_html=True 
        )
    
    if show:
        # Mostrar
        fig.show()

#################################################################################################################
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import polars as pl

def barplot_01b(
    df, x, y, orientation='h', color=None, 
    barmode=None,
    yticks_color_column=None,     
    yticks_color_map=None,  
    color_discrete_map=None, hover_data=None, 
    labels=None, hovertemplate=None, 
    category_orders=None, title=None,
    plot_save_path=None, show=None, height=800,
    facet_col=None,
    reverse_y_order=False,
    # --- CONFIGURACIÓN DE TAMAÑOS ---
    x_ticks_size=14, x_title_size=16, 
    y_ticks_size=14, y_title_size=16,
    title_size=20,       
    legend_size=13,      
    legend_title_size=15 
    ):

    # Configuración base del Layout
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
    
    # -------------------------------------------------------------------------
    # CASO 1: SIN FACET (Comportamiento Estándar)
    # -------------------------------------------------------------------------
    if not facet_col:
        tick_vals, tick_text = None, None
        
        # 1. Calcular orden y ORDENAR EL DF
        if yticks_color_column and yticks_color_map:
            stats_df = (
                df.group_by(y)
                .agg([
                    pl.col(x).sum().alias("total_metric"),       
                    pl.col(yticks_color_column).first().alias("region_name") 
                ])
                .sort("total_metric", descending=False if not reverse_y_order else True) 
            )
            ordered_items = stats_df[y].to_list()
            ordered_regions = stats_df["region_name"].to_list()
            
            df_sorted = df.sort(x, descending=False if not reverse_y_order else True)
            
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
            df_sorted = df
            ordered_items = None
            tick_vals = None

        # 2. Crear Gráfico
        fig = px.bar(
            df_sorted, x=x, y=y, orientation=orientation, color=color,
            barmode=barmode, title=title, hover_data=hover_data,
            color_discrete_map=color_discrete_map,
            labels=labels
        )
        
        # 3. Estilos Eje Y
        y_axis_config = dict(
            tickfont=dict(size=y_ticks_size),
            title_font=dict(size=y_title_size),
            automargin=True # Asegura espacio para etiquetas largas
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

        # 4. Estilos Eje X
        fig.update_xaxes(
            tickfont=dict(size=x_ticks_size),       
            title_font=dict(size=x_title_size),     
            showgrid=True, gridcolor='#f0f0f0'
        )

    # -------------------------------------------------------------------------
    # CASO 2: CON FACET_COL (Modo Orden Independiente)
    # -------------------------------------------------------------------------
    else:
        facet_vals = df[facet_col].unique().to_list()
        facet_vals.sort() 

        fig = make_subplots(
            rows=1, cols=len(facet_vals), 
            subplot_titles=facet_vals,
            shared_yaxes=False,   
            horizontal_spacing=0.15 
        )

        seen_legends = set()

        for i, val in enumerate(facet_vals):
            sub_df = df.filter(pl.col(facet_col) == val)
            
            current_tick_vals = None
            current_tick_text = None
            
            # 1. Calcular orden
            if yticks_color_column and yticks_color_map:
                stats_df = (
                    sub_df.group_by(y)
                    .agg([
                        pl.col(x).sum().alias("total_metric"),       
                        pl.col(yticks_color_column).first().alias("region_name") 
                    ])
                    .sort("total_metric", descending=False if not reverse_y_order else True)
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
            
            # 2. Ordenar DF
            sub_df_sorted = sub_df.sort(x, descending=False if not reverse_y_order else True)

            # 3. Generar trazas
            aux_fig = px.bar(
                sub_df_sorted, x=x, y=y, orientation=orientation, color=color,
                color_discrete_map=color_discrete_map,
                hover_data=hover_data, labels=labels
            )
            
            for trace in aux_fig.data:
                trace_name = trace.name 
                if trace_name not in seen_legends:
                    trace.showlegend = True
                    seen_legends.add(trace_name)
                else:
                    trace.showlegend = False
                fig.add_trace(trace, row=1, col=i+1)
            
            # 4. Actualizar Eje Y (AQUÍ ESTABA EL ERROR)
            y_update_args = dict(
                row=1, col=i+1,
                showgrid=False,
                tickfont=dict(size=y_ticks_size),
                title_font=dict(size=y_title_size),
                # --- NUEVO: AÑADIMOS EL TEXTO DEL TÍTULO EXPLÍCITAMENTE ---
                title_text=labels.get(y, y) if labels else y,
                automargin=True # Importante para que no se coma el texto
            )
            
            if current_tick_vals and current_tick_text:
                y_update_args.update(dict(
                    tickmode='array', 
                    tickvals=current_tick_vals, 
                    ticktext=current_tick_text,
                    type='category', 
                    categoryorder='array', 
                    categoryarray=current_tick_vals 
                ))
            
            fig.update_yaxes(**y_update_args)
            
            # 5. Actualizar Eje X
            fig.update_xaxes(
                title_text=labels.get(x, x) if labels else x,
                row=1, col=i+1, 
                showgrid=True, gridcolor='#f0f0f0',
                tickfont=dict(size=x_ticks_size),
                title_font=dict(size=x_title_size)
            )

    # -------------------------------------------------------------------------
    # AJUSTES FINALES
    # -------------------------------------------------------------------------
    fig.update_traces(hovertemplate=hovertemplate)
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    
    fig.update_layout(**layout_args)

    if plot_save_path:
        fig.write_html(plot_save_path, include_plotlyjs='cdn', full_html=True)
    
    if show:
        fig.show()
                
#################################################################################################################   