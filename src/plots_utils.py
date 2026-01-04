import plotly.express as px

def time_series_plot(
        df, x, y, title=None, line_group=None, color=None, 
        color_discrete_map=None, category_orders=None, 
        hover_name=None, hover_data=None, labels=None, 
        hovertemplate=None, plot_save_path=None, show=True
    ):

    # Crear el gráfico de líneas
    fig = px.line(
        df,              # Tu dataframe filtrado
        x=x,             # Eje X
        y=y,   # Eje Y (según tu imagen)
        color=color,      
        line_group=line_group,
        hover_name=hover_name,
        title=title,
        hover_data=hover_data, # Información extra al pasar el ratón
        markers=True,         # Pone puntitos en cada año para ver mejor los datos reales
        category_orders=category_orders, 
        color_discrete_map=color_discrete_map, 
        labels=labels
    )

    fig.update_traces(
        hovertemplate=hovertemplate
    )

    # Mejoras de Layout  
    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=14), 
            title_font=dict(size=16)
            ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='lightgray',
            tickfont=dict(size=14), 
            title_font=dict(size=16)            
            ),
        plot_bgcolor='white',
        height=600,  # Altura del gráfico

        title=dict(
            text=f"<b>{title}</b>" if title else None, # Inyectamos HTML para negrita
            font=dict(size=20),
            x=0.5, # Opcional: Centrar título (si no te gusta, borra esta línea)
            xanchor='center'
        ),
        
        legend=dict(
            font=dict(size=13),
            title_font=dict(size=15) # El título de la leyenda un pelín más grande
        )
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

def barplot(
    df, x, y, orientation=None, color=None, 
    color_discrete_map=None, hover_data=None, 
    labels=None, hovertemplate=None, 
    category_orders=None, title=None,
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
        height=600,                # Altura ajustada a la cantidad de países
        xaxis=dict(
            showgrid=True, 
            gridcolor='#f0f0f0',
            #side='top',           
            tickfont=dict(size=14), 
            title_font=dict(size=16)
        ),
        yaxis=dict(
            showgrid=False,
            categoryorder='total ascending',
            tickfont=dict(size=14), 
            title_font=dict(size=16)  
        ),
        title=dict(
            text=f"<b>{title}</b>" if title else None, # Inyectamos HTML para negrita
            font=dict(size=20),
            x=0.5, # Opcional: Centrar título (si no te gusta, borra esta línea)
            xanchor='center'
        ),
        legend=dict(
            font=dict(size=13),
            title_font=dict(size=15) # El título de la leyenda un pelín más grande
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