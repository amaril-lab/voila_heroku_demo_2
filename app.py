import os
import pandas as pd
#import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash import dcc
import dash
import dash_core_components as dcc

from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np

sum_all=  pd.read_excel('df_hosp_waste.xlsx')
del sum_all["Unnamed: 0"]

sum_all = sum_all.rename(columns={"result": "raw wastewater epidemiology"})
cities = sum_all.LocationName.unique()
available_indicators =sum_all.columns[2:6]
df_name = (sum_all.groupby(['LocationName'])["time"].count().reset_index()).sort_values(by= "time", ascending = False)

#df_name["LocationName"] = [ i[::-1] for i in list(df_name["LocationName"])]
df_name.rename(columns={'time':'Number of observations'}, inplace=True)
bar_fig  = px.bar(df_name.sort_values(by=['Number of observations']), x="LocationName", y=["Number of observations"], 
                  title="Number of observations per city",template = 'plotly_dark')

bar_fig.update_layout(showlegend=False)
fig_map = px.scatter_mapbox(sum_all, lat="city_latitude", lon="city_longitude",
            color = "hosp_cum", size = "raw wastewater epidemiology",
            size_max=40, zoom=6,mapbox_style="open-street-map",animation_frame = 'time', template = "plotly_dark",
            title = 'COVID19 in wastewater over time <br><sup>Size represents the amount of virus, color represents the number of verified</sup> ', )
fig_map = fig_map.update_layout(transition = {'duration': 10},plot_bgcolor='#000000',showlegend=False,width=700,height=700)





external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.config.suppress_callback_exceptions = True

#du.configure_upload(app, r"C:\Users\Haim\Desktop\covid")

# Create server variable with Flask server object for use with gunicorn
server = app.server

      
colors = {'background': 'black','text': '#FFD700'}
#server = app.server
app.layout =html.Div(style={'backgroundColor': colors['background']},
    children=[html.Div(style={'backgroundColor': colors['background']},
            children=[
                dcc.Graph(figure = bar_fig),
            ],className='row'),

              
html.Div(style={'backgroundColor': colors['background']},                 
                children=[
                html.Div('Select the variables for the X-axis and the Y-axis', style={'color': '#FFD700', 'fontSize': 14}),
                html.Div('X-axis=', style={'color': '#FFD700', 'fontSize': 14}),
               
                dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='raw wastewater epidemiology',
                style=dict(width='40%',display= 'inline-block'),

                    
            ),]),
              
html.Div(style={'backgroundColor': colors['background']},                 
        children=[            
            html.Div('Y-axis=', style={'color': '#FFD700', 'fontSize': 14}),
    
            dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='infected',
                style=dict(width='40%', display= 'inline-block')
            )]),
              
html.Div(style={'backgroundColor': colors['background']}, 
          children=[
              html.Div('Pick one of the cities dropdown below.', style={'color': '#FFD700', 'fontSize': 14}),
         
                dcc.Dropdown(id="dropdown_city",
                             options=[{"label": x, "value": x} for x in cities],
                             value=cities[0],
                             clearable=False,
                             style=dict(width='50%')
                            ),
            
                dcc.Graph(id="line-plot",
                         animate=True,className='row'),
                
                

            ]),
html.Div(style={'backgroundColor': colors['background']},
         children=[    
                dcc.Graph(figure = fig_map,className='six columns'),
                dcc.Graph(id="scatter-plot",className='six columns'),
                
         ]),  
              
    ]
)



@app.callback(
    Output("line-plot", "figure"),
    [Input("dropdown_city", "value")],
    Input('crossfilter-xaxis-column', 'value'),
    Input('crossfilter-yaxis-column', 'value')
     )
def update_line(V,xaxis_column_name, yaxis_column_name):
    mask = sum_all[ (sum_all["LocationName"] == V)]
    mask["raw wastewater epidemiology"] = mask["raw wastewater epidemiology"].astype(float)
    mask = pd.melt(mask[["raw wastewater epidemiology","hosp", "hosp_cum", "infected", "time"]])
    fig = px.line(x=mask[mask['variable'] == "time"]["value"], y=[mask[mask['variable'] == xaxis_column_name]['value'], mask[mask['variable'] == yaxis_column_name]["value"]] ,
              template = 'plotly_dark',title ="Relationship between wastewater and infected cases") 
    
    newnames={'wide_variable_0':xaxis_column_name , 'wide_variable_1':yaxis_column_name}
    
    #fig.write_html(buffer)
    fig.update_layout(showlegend=False,width=1200,height=600)
    

    return fig





@app.callback(
    Output("scatter-plot", "figure"),
    [Input("dropdown_city", "value")],
    Input('crossfilter-xaxis-column', 'value'),
     Input('crossfilter-yaxis-column', 'value')
     )
    
def update_scatter(V,xaxis_column_name, yaxis_column_name):
    mask = sum_all[ (sum_all["LocationName"] == V)]
    mask["raw wastewater epidemiology"] = mask["raw wastewater epidemiology"].astype(float)
    mask = pd.melt(mask[["raw wastewater epidemiology","hosp", "hosp_cum", "infected"]])
    
    
    fig1 = px.scatter(mask ,x=mask[mask['variable'] == xaxis_column_name]['value'], y =mask[mask['variable'] == yaxis_column_name]['value'] ,template = 'plotly_dark'  ,title = "wastewater vs infected cases for the selected city")
    fig1.update_layout(showlegend=False,width=600,height=700)  
    fig1.update_xaxes(title=xaxis_column_name)
    fig1.update_yaxes(title=yaxis_column_name)

                                           
    return fig1


if __name__ == '__main__':
    app.run_server(debug=True)

