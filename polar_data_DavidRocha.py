import plotly.express as px
import datetime
import json
import time
import os
import numpy as np
import glob
import pandas as pd
from pandas.io.json import json_normalize

# ------------------------------------------------------------------------------
# Import and clean data (importing jsons into pandas)

current_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(current_path)
Filelist = [file for file in os.listdir(
    current_path) if file.endswith('.json')]

struct = []
for i in Filelist:
    with open(i) as tempfile:
        data = json.load(tempfile)
        struct.append(data)

MBs = list()
for l in struct:
    df = pd.json_normalize(data=l, max_level=1)
    MBs.append(df)

df = pd.concat(MBs)

df['exercises'] = [pd.json_normalize(data=i, max_level=1) for i in df['exercises']]

df.reset_index(drop=True, inplace=True)

lst = []

for index, values in df['exercises'].items():
    exercise = values
    df_exerc = pd.DataFrame(exercise)
    lst.append(df_exerc)

exercises_df = pd.concat(lst, axis=0)

exercises_df.reset_index(drop=True, inplace=True)

not_in = exercises_df[~exercises_df['startTime'].isin(df['startTime'])]

corrections = ['2016-04-16T17:41:43.000', '2016-10-19T20:53:43.000']

indexes = [33, 113]

for x, y in zip(indexes, corrections):
    exercises_df.loc[x, 'startTime'] = y


df = df.merge(exercises_df, on='startTime')
df = df[df.columns.drop(list(df.filter(regex='_y')))]
df.columns = df.columns.str.rstrip('_x')

for i in df.filter(regex='Time').columns.to_list():
    df[i] = pd.to_datetime(df[i])
    

for i in list(set(df['sport'].to_list())):
    
    globals()["df_" + str(i)] = df[df['sport'] == i]
    
for i in [i for i in list(globals()) if i.startswith('df_')]:
    globals()[i].reset_index(drop=True, inplace=True)


# -----------------------------------------------------------------------------
#functions metrics for nested columns ()

def avg_dict_col(df, column):
    for index, value in df[column].items():
        lst_dfs = [pd.json_normalize(data=value, max_level=1) if value is not np.nan
                   else np.nan for value in df[column]]
        lst_series = pd.Series(lst_dfs)
        avg_series = [i['value'].mean() if
                          isinstance(i, pd.DataFrame) and 'value' in i.columns else 0 for i in lst_series]
        df[column + '_mean'] = avg_series

def min_dict_col(df, column):
    for index, value in df[column].items():
        lst_dfs = [pd.json_normalize(data=value, max_level=1) if value is not np.nan
                   else np.nan for value in df[column]]
        lst_series = pd.Series(lst_dfs)
        min_series = [i['value'].min() if
                      isinstance(i, pd.DataFrame) and 'value' in i.columns else 0 for i in lst_series]
        df[column + '_min'] = min_series


def max_dict_col(df, column):
    for index, value in df[column].items():
        lst_dfs = [pd.json_normalize(data=value, max_level=1) if value is not np.nan
                   else np.nan for value in df[column]]
        lst_series = pd.Series(lst_dfs)
        max_series = [i['value'].max() if
                          isinstance(i, pd.DataFrame) and 'value' in i.columns else 0 for i in lst_series]
        df[column + '_mean'] = max_series
        
        
def median_dict_col(df, column):
    for index, value in df[column].items():
        lst_dfs = [pd.json_normalize(data=value, max_level=1) if value is not np.nan
                   else np.nan for value in df[column]]
        lst_series = pd.Series(lst_dfs)
        median_series = [i['value'].median() if
                      isinstance(i, pd.DataFrame) and 'value' in i.columns else 0 for i in lst_series]
        df[column + '_mean'] = median_series


# -----------------------------------------------------------------------------
# generate metrics

avg_dict_col(df_RUNNING, 'samples.heartRate')

avg_dict_col(df_RUNNING, 'samples.speed')

avg_dict_col(df_RUNNING, 'samples.cadence')

df_count_per_sport = df.groupby(by='sport', as_index=False).agg({'startTime': pd.Series.nunique})

df_route_1 = pd.json_normalize(data=df_RUNNING.loc[1, 'samples.recordedRoute'], max_level=1)

df_speed_1 = pd.json_normalize(data=df_RUNNING.loc[1, 'samples.speed'], max_level=1)

df_heart_1 = pd.json_normalize(data=df_RUNNING.loc[1, 'samples.heartRate'], max_level=1)

df_heart_speed_1 = df_heart_1.merge(df_speed_1, on='dateTime', suffixes=['_heart', '_speed'])

df_zones_heart_rate_1 = df_speed_1 = pd.json_normalize(data=df_RUNNING.loc[1, 'zones.heart_rate'], max_level=1)

# ------------------------------------------------------------------------------
# Graphs

#---Basic

map_all_152 = px.scatter_mapbox(df, lat="latitude", lon="longitude", color='sport', title='Mapa', mapbox_style='carto-positron', zoom=2, center={'lat': -15.79413, 'lon': -47.882455})

count_per_sport = px.bar(df_count_per_sport, x='sport', y='startTime', title='Quantidade de atividades por esporte', color='sport')

dist_per_sport = px.box(df, x='sport', y='distance', color='sport', title='Distância percorrida por tipo de esporte')

calories_per_sport = px.box(df, x='sport', y='kiloCalories', color='sport', title='Calorias gastas por tipo de esporte')

weight = px.line(df, x='startTime', y='physicalInformationSnapshot.weight, kg', title='Variação do peso ao longo do ano')

vo2_max = px.line(df, x='startTime', y='physicalInformationSnapshot.vo2Ma', title='Variação do vO2 max ao longo do ano')

max_heart_rate = px.line(df, x='startTime', y='physicalInformationSnapshot.maximumHeartRate', title='Variação da max_heart_rate ao longo do ano')

rest_heart_rate = px.line(df, x='startTime', y='physicalInformationSnapshot.restingHeartRate', title='Variação da rest_heart_rate ao longo do ano')

aerobic_threshold = px.line(df, x='startTime', y='physicalInformationSnapshot.aerobicThreshold', title='Variação do limite aeróbico ao longo do ano')

anaerobic_threshold = px.line(df, x='startTime', y='physicalInformationSnapshot.anaerobicThreshold', title='Variação do limite anaeróbico ao longo do ano')

#---RUNNING

map_running = px.scatter_mapbox(df_route_1, lat="latitude", lon="longitude", color='altitude', title='Mapa Corrida', mapbox_style='carto-positron', zoom=2)

mean_heart = px.scatter(df_RUNNING, x='startTime', y='samples.heartRate_mean')

#---1 Run

map_route_1 = px.scatter_mapbox(df_route_1, lat="latitude", lon="longitude", color='altitude', title='Mapa', mapbox_style='carto-positron', zoom=12)

heart_speed = px.line(df_heart_speed_1, x='dateTime', y=['value_heart','value_speed'], title='BPS x velocidade')

geopos_3d = px.line_3d(df_route_1, x="latitude", y="longitude", z='altitude', color='altitude', title='Geoposition x Elevation')

aerobic = px.line(df_heart_1, x='dateTime', y='value', title='Limite de exercício aeróbico')
aerobic.update_layout(shapes=[dict(type='line', yref='y', y0=149, y1=149, xref='paper', x0=0, x1=1), dict(type='line', yref='y', y0=178, y1=178, xref='paper', x0=0, x1=1)])


# ------------------------------------------------------------------------------
# Dash App layout

import plotly.graph_objects as go
import dash  # (version 1.14.0)
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets) 

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H2('Hackaton IESB'),
            dcc.Graph(id='map_all', figure=map_all_152),
            dcc.Graph(id='dist_per_sport', figure=dist_per_sport),
            dcc.Graph(id='weight', figure=weight),
            dcc.Graph(id='max_heart_rate', figure=max_heart_rate),
            dcc.Graph(id='aerobic_threshold', figure=aerobic_threshold),
            dcc.Graph(id='map_route', figure=map_route_1),
            dcc.Graph(id='heart_speed', figure=heart_speed)
        ], className="six columns"),

        html.Div([
            html.H2('Polar Dataset 2016'),
            dcc.Graph(id='count_per_sport', figure=count_per_sport),
            dcc.Graph(id='calories_per_sport', figure=calories_per_sport),
            dcc.Graph(id='vo2Ma', figure=vo2_max),
            dcc.Graph(id='rest_heart_rate', figure=rest_heart_rate),
            dcc.Graph(id='anaerobic_threshold', figure=anaerobic_threshold),
            dcc.Graph(id='geo_pos_3d', figure=geopos_3d),
            dcc.Graph(id='aerobic', figure=aerobic)
        ], className="six columns"),
    ], className="row")

])

if __name__ == '__main__':
    app.run_server(debug=True)
