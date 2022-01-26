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


df0 = pd.read_csv('cleandf.spatial_data.csv')
print (df0.columns)
df0= df0[['Dose_number', 'Count', 'city_desc','Religion_Desc', 'arab_rate',
     'ortodox_rate', 'relevant_desk', 'perc', 'count_nonvac_young', 'count_age_old', 'diff', 'skewfirst',
       'skewsecond', 'kurfirst', 'kursecond', 'meanfirst', 'stdfirst',
       'meanthird', 'stdthird', 'meanlast', 'stdlast', 'meanrisk1', 'stdrisk1',
       'meanrisk3', 'stdrisk2', 'meanimmunity', 'stdimmunity', 'hosp_total',
       'recovered_total', 'death_total', 'positive_total', 'recavored_norm', 'hosp_norm', 'positive_norm',
       'death_norm', 'anomaly']]


df = pd.read_csv('AgglomerativeClustering_n10_knn_011220_081221.csv')
del df["id_num"]
del df["city_from"]
del df["connected_component"]
del df["an"]
df = df.merge(df0, left_on='city_name', right_on='city_desc')
del df["city_desc"]
df.head()
df["perc"] = df["perc"]*100 
df["hosp_norm"] = df["hosp_norm"]*100 
df["positive_norm"] = df["positive_norm"]*100 
df["death_norm"] = df["death_norm"]*100 
df["meanimmunity"] = df["meanimmunity"]*100 
df["stdimmunity"] = df["stdimmunity"]*100 
df["diff"] = df["diff"]*100 
df["count_age_old"] = df["count_age_old"]*100 
df["count_nonvac_young"] = df["count_nonvac_young"]*100 
df['meanimmunity'] =  df['meanimmunity'].fillna(0)
df['size'] =  0.1
df["clusters"] = df["clusters"].astype(str)

df1 = pd.melt(df, id_vars=['city_name',"city_longitude","city_latitude", "size", "relevant_desk"], value_vars=["clusters",'perc', 'count_nonvac_young',
       'count_age_old', 'diff','meanfirst', 'meanthird', 'meanlast', 'meanrisk1', 'meanrisk3'
        ,"meanimmunity",'stdimmunity', 'hosp_total', 'death_total', 'positive_total',  'hosp_norm',
       'positive_norm', 'death_norm'])



#buffer = io.StringIO()
#html_bytes = buffer.getvalue().encode()
#encoded = b64encode(html_bytes).decode()

cities = df1.city_name.unique()
#opclass = df1.clusters.unique()
available_indicators = df1['variable'].unique()
lst_col0 = ['meanfirst', 'meanthird', 'meanlast', 'meanrisk1', 'meanrisk3','hosp_total', 'death_total', 'positive_total']
lst_col =['perc', 'count_nonvac_young','count_age_old', 'diff', 'meanimmunity', 'stdimmunity',  'hosp_norm','positive_norm', 'death_norm']



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.config.suppress_callback_exceptions = True

#du.configure_upload(app, r"C:\Users\Haim\Desktop\covid")

# Create server variable with Flask server object for use with gunicorn
server = app.server
app.layout = html.Div([
    
    html.Div([
        dcc.Dropdown(
        id="dropdown_indicators",
        options=[{'label': i, 'value': i} for i in available_indicators],
        value=available_indicators[0],
        clearable=False,
        style=dict(
                    width='70%',
                    verticalAlign="middle")
        ), 
        
        dcc.Graph(id="MapPlot"),
        #html.A(
        #html.Button("Download HTML"), 
        #id="download",
        #href="data:text/html;base64," +encoded,
        #download="plotly_graph.html"
    #)
    ], className="one-third column",
    style={'width': '50%' ,'display': 'inline-block','padding': '0 20'}
    ),  
    
    html.Div([
        dcc.Dropdown(
        id="dropdown_city",
        options=[{"label": x, "value": x} for x in cities],
        value=cities[0],
        clearable=False,
        ),
        dcc.Graph(id="x-bar-chart"),
        dcc.Graph(id="y-bar-chart"),
        #      dcc.Graph(id="tbl", )
    
    ],
    className="one-third column",
    style={'width': '40%', 'display': 'inline-block' }
    )
    
    ])


@app.callback(
    Output("MapPlot", "figure"),
    [Input("dropdown_indicators", "value")])
def update_scatter_mapbox(V):
    mask = df1[ (df1["variable"] == V)]
    if V != "clusters":
        mask["value"] = mask["value"].astype(float)  
    fig = px.scatter_mapbox(mask, lat="city_latitude", lon="city_longitude",
            color="value",zoom=5, text="city_name",mapbox_style="open-street-map")
    #fig.write_html(buffer)
    fig.update_layout(showlegend=False,width=500,height=700)  
    return fig

@app.callback(
    Output("x-bar-chart", "figure"), 
    [Input("dropdown_city", "value")])
def update_bar_chart(city):
    mask = df1[ (df1["city_name"] == city) & (df1["variable"].isin(lst_col))]
    
    fig1 = px.bar(mask, x="variable", y="value", color="city_name")
    fig1.update_layout(showlegend=False,width=500,height=300)
    
    return fig1
@app.callback(
    Output("y-bar-chart", "figure"), 
    [Input("dropdown_city", "value")])
def update_bar_chart(city):
    mask = df1[ (df1["city_name"] == city) & (df1["variable"].isin(lst_col0))]
    
    fig2 = px.bar(mask, x="variable", y="value", color="city_name")
    fig2.update_layout(showlegend=False,width=500,height=300)
    
    return fig2


if __name__ == '__main__':
    app.run_server(debug=True)

