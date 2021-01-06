import plotly.express as px
import datetime
import json
import time
import pathlib
import os
import numpy as np
import glob
import pandas as pd
from pandas.io.json import json_normalize

# ------------------------------------------------------------------------------
# Import and clean data (importing jsons into pandas)

current_path = pathlib.Path(__file__).parent.absolute()
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

sports_list = list(set(df['sport'].to_list()))
    
# --------------------------------------------------------------
# static graphs

map_all_152 = px.scatter_mapbox(df, lat="latitude", lon="longitude", color='sport', title='Map - All activities', 
                                mapbox_style='carto-positron', zoom=2, center={'lat': -15.79413, 'lon': -47.882455}, template='plotly_dark')

df_count_per_sport = df.groupby(by='sport', as_index=False).agg({'startTime': pd.Series.nunique})
count_per_sport = px.bar(df_count_per_sport, x='sport', y='startTime', title='Number of activities per sport', color='sport', template='plotly_dark')

dist_per_sport = px.box(df, x='sport', y='distance', color='sport', title='Distance per sport', template='plotly_dark')

calories_per_sport = px.box(df, x='sport', y='kiloCalories', color='sport', title='Calories per sport', template='plotly_dark')

weight = px.line(df, x='startTime', y='physicalInformationSnapshot.weight, kg', title='Weight', template='plotly_dark')

vo2_max = px.line(df, x='startTime', y='physicalInformationSnapshot.vo2Ma', title='Maximum VO2', template='plotly_dark')

max_heart_rate = px.line(df, x='startTime', y='physicalInformationSnapshot.maximumHeartRate', title='Maximum heart rate', template='plotly_dark')

rest_heart_rate = px.line(df, x='startTime', y='physicalInformationSnapshot.restingHeartRate', title='Rest heart rate', template='plotly_dark')

aerobic_threshold = px.line(df, x='startTime', y='physicalInformationSnapshot.aerobicThreshold', title='Aerobic threshold', template='plotly_dark')

anaerobic_threshold = px.line(df, x='startTime', y='physicalInformationSnapshot.anaerobicThreshold', title='Anaerobic threshold', template='plotly_dark')

emp = px.scatter(x=['Select items'], y=['Select items'], template='plotly_dark')


# -------------------------------------------------------------
# Dash app

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_table
import plotly.graph_objects as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

colors = {
    'background': '#111111',
    'text': '#FFFFFF'
}

# ---------------------
# tab1 layout
tab1_layout = html.Div([
    html.H1(
        children='_________________________________________',
        style={
            'textAlign' : 'center',
            'color': colors['text'],
            'backgroundColor': colors['background']
        }
    ),
    
    dcc.Graph(id='map1', figure=map_all_152, style={'height':'75vh'}),
    dcc.Graph(id='count_per_sport', figure=count_per_sport),
    
    html.Div([
        html.Div([
            dcc.Graph(id='dist_per_sport', figure=dist_per_sport),
            dcc.Graph(id='weight', figure=weight),
            dcc.Graph(id='max_heart_rate', figure=max_heart_rate),
            dcc.Graph(id='aerobic_threshold', figure=aerobic_threshold),
        ], className='six columns', style={'width': '50%'}),
        
        html.Div([
            dcc.Graph(id='calories_per_sport', figure=calories_per_sport),
            dcc.Graph(id='vo2_max', figure=vo2_max),
            dcc.Graph(id='rest_heart_rate', figure=rest_heart_rate),
            dcc.Graph(id='anaerobic_threshold', figure=anaerobic_threshold),
        ], className='six columns', style={'width': '50%', 'marginLeft': '0'}),
    ], style={'backgroundColor': colors['background'], 'color': colors['text']}),
    
], style={'backgroundColor': colors['background'], 'color': colors['text']}),


# --------------------
# tab2 layout 
tab2_layout = html.Div([
    
    html.Div([
        html.H3(
            children='Select a sport',
            style={
            'textAlign' : 'center',
            'color': colors['text']
            }
        ),
        dcc.Dropdown(
            id='drop_sports',
            options=[{'label': i, 'value': i} for i in sports_list],
            style={
                'textAlign' : 'center',
                'color' : 'black',
                'backgroundColor' : 'black',
            }
        ),
        html.H3(
            children='Select an activity (by date)',
            style={
                'textAlign' : 'center',
                'color': colors['text']
            }
        ),
        dcc.Dropdown(
            id='drop_activities',
            style={
                'textAlign' : 'center',
                'color': 'black',
                'backgroundColor': 'black',
            }
        ),
    ]),
            
    html.Div([
        html.Div([
            html.H5(
                children='Total time',
                style={
                    'textAlign' : 'center',
                    'color': colors['text'],
                    'backgroundColor': colors['background'],
                    'width': '100%',
                    'height': '8vh',
                } 
            ),
            html.H6(
                id='time',
                children='_______',
                style={
                    'textAlign' : 'center',
                    'color': colors['text'],
                    'backgroundColor': colors['background'],
                    'width': '100%',
                    'height': '8vh',
                } 
            ),
            html.H5(
                children='Total Distance',
                style={
                    'textAlign' : 'center',
                    'color': colors['text'],
                    'backgroundColor': colors['background'],
                    'width': '100%',
                    'height': '8vh',
                } 
            ),
            html.H6(
                id='distance',
                children='_______',
                style={
                    'textAlign' : 'center',
                    'color': colors['text'],
                    'backgroundColor': colors['background'],
                    'width': '100%',
                    'height': '8vh',
                } 
            ),
            html.H5(
                children='Calories burned',
                style={
                    'textAlign' : 'center',
                    'color': colors['text'],
                    'backgroundColor': colors['background'],
                    'width': '100%',
                    'height': '8vh',
                } 
            ),
            html.H6(
                id='calories',
                children='_______',
                style={
                    'textAlign' : 'center',
                    'color': colors['text'],
                    'backgroundColor': colors['background'],
                    'width': '100%',
                    'height': '8vh',
                } 
            ),
            html.H5(
                children='Mean Cadence',
                style={
                    'textAlign' : 'center',
                    'color': colors['text'],
                    'backgroundColor': colors['background'],
                    'width': '100%',
                    'height': '8vh',
                } 
            ),
            html.H6(
                id='cadence',
                children='_______',
                style={
                    'textAlign' : 'center',
                    'color': colors['text'],
                    'backgroundColor': colors['background'],
                    'width': '100%',
                    'height': '8vh',
                } 
            ),
        ], className='three columns', style={'backgroundColor': colors['background'], 'color': colors['text'], 'marginRight': '0', 'marginBottom':'0'}),
                    
        html.Div([
            dcc.Graph(id='graph1', figure=emp, style={'height':'70vh'}),
        ], className='nine columns', style={'backgroundColor': colors['background'], 'color': colors['text'], 'marginLeft': '0', 'marginRight': '0'}),
                    
    ], className='twelve columns', style={'backgroundColor': colors['background'], 'color': colors['text']}),
                
    html.Div([
        html.Div([
            dcc.Graph(id='graph2', figure=emp),
            dcc.Graph(id='graph4', figure=emp),
            dcc.Graph(id='graph6', figure=emp),
        ], className='six columns', style={'width': '50%'}),
        
        html.Div([
            dcc.Graph(id='graph3', figure=emp),
            dcc.Graph(id='graph5', figure=emp),
            dcc.Graph(id='graph7', figure=emp),
        ], className='six columns', style={'width': '50%', 'marginLeft': '0'}),
        
    ],className='twelve columns', style={'backgroundColor': colors['background'], 'color': colors['text']})
        
]),

# --------------------
# tab2 callbacks

@app.callback(
    dash.dependencies.Output('drop_activities', 'options'),
    [dash.dependencies.Input('drop_sports', 'value')]
)

def update_drop_activities(sport):
    
    if sport is None:
        raise PreventUpdate
    else:
        df_sport = df[df['sport'] == sport]
        activities_list = df_sport['startTime'].to_numpy('datetime64')
        return [{'label': str(i), 'value': str(i)} for i in activities_list]


@app.callback(
    [dash.dependencies.Output('time', 'children'),
    dash.dependencies.Output('distance', 'children'),
    dash.dependencies.Output('calories', 'children'),
    dash.dependencies.Output('cadence', 'children')],
    [dash.dependencies.Input('drop_activities', 'value')]
)

def update_side_bar(activity):
    
    if activity is None:
        raise PreventUpdate       
    else:
        filtered_df = df[df['startTime'] == activity]
        time = filtered_df['stopTime'] - filtered_df['startTime']
        distance = filtered_df['distance']
        calories = filtered_df['kiloCalories']
        cadence = filtered_df['cadence.avg']
        
        return time, distance, calories, cadence

@app.callback(
    dash.dependencies.Output('graph1', 'figure'),
     dash.dependencies.Input('drop_activities', 'value')
)

def update_map(activity):
    
    if activity is None:
        raise PreventUpdate
           
    else:

        filtered_df = df[df['startTime'] == activity]
        
        if filtered_df['samples.recordedRoute'].isnull().values.any():
            
            return px.scatter(x=['Not available'], y=['Not available'], title='Map', template='plotly_dark')
        
        else:
            route_df = pd.json_normalize(data=filtered_df.iloc[0]['samples.recordedRoute'], max_level=1)
            map_activ = px.line_mapbox(route_df, lat="latitude", lon="longitude", title='Map', 
                                          mapbox_style='carto-positron', zoom=12, template='plotly_dark')
            
            return map_activ

@app.callback(
    dash.dependencies.Output('graph2', 'figure'),
    dash.dependencies.Input('drop_activities', 'value')
)

def update_distance(activity):
    
    if activity is None:
        raise PreventUpdate
           
    else:

        filtered_df = df[df['startTime'] == activity]
        
        if filtered_df['samples.distance'].isnull().values.any():
            
            return px.scatter(x=['Not available'], y=['Not available'], title='Distance', template='plotly_dark')
        
        else:
            distance_df = pd.json_normalize(data=filtered_df.iloc[0]['samples.distance'], max_level=1)
            
            if distance_df.shape[1] == 2:
                distance = px.scatter(distance_df, x='dateTime', y='value', color='value', title='Distance', template='plotly_dark')
            
                return distance
            
            else:
                
                return px.scatter(x=['Not available'], y=['Not available'], title='Distance', template='plotly_dark')

@app.callback(
    dash.dependencies.Output('graph3', 'figure'),
    dash.dependencies.Input('drop_activities', 'value')
)

def update_altitude(activity):
    
    if activity is None:
        raise PreventUpdate
           
    else:

        filtered_df = df[df['startTime'] == activity]
        
        if filtered_df['samples.altitude'].isnull().values.any():
            
            return px.scatter(x=['Not available'], y=['Not available'], title='Altitude', template='plotly_dark')
        
        else:
            altitude_df = pd.json_normalize(data=filtered_df.iloc[0]['samples.altitude'], max_level=1)
            
            if altitude_df.shape[1] == 2:
                altitude = px.scatter(altitude_df, x='dateTime', y='value', title='Altitude', template='plotly_dark', 
                                      color='value')
            
                return altitude
            
            else:
                
                return px.scatter(x=['Not available'], y=['Not available'], title='Altitude', template='plotly_dark')

@app.callback(
    dash.dependencies.Output('graph4', 'figure'),
    dash.dependencies.Input('drop_activities', 'value')
)

def update_speed(activity):
    
    if activity is None:
        raise PreventUpdate
           
    else:

        filtered_df = df[df['startTime'] == activity]
        
        if filtered_df['samples.speed'].isnull().values.any():
            
            return px.scatter(x=['Not available'], y=['Not available'], title='Speed', template='plotly_dark')
        
        else:
            speed_df = pd.json_normalize(data=filtered_df.iloc[0]['samples.speed'], max_level=1)
            
            if speed_df.shape[1] == 2:
                speed = px.scatter(speed_df, x='dateTime', y='value', title='Speed', template='plotly_dark', 
                                      color='value')
            
                return speed
            
            else:
                
                return px.scatter(x=['Not available'], y=['Not available'], title='Speed', template='plotly_dark')


@app.callback(
    dash.dependencies.Output('graph5', 'figure'),
    dash.dependencies.Input('drop_activities', 'value')
)

def update_cadence(activity):
    
    if activity is None:
        raise PreventUpdate
           
    else:

        filtered_df = df[df['startTime'] == activity]
        
        if filtered_df['samples.cadence'].isnull().values.any():
            
            return px.scatter(x=['Not available'], y=['Not available'], title='Cadence', template='plotly_dark')
        
        else:
            cadence_df = pd.json_normalize(data=filtered_df.iloc[0]['samples.cadence'], max_level=1)
            
            if cadence_df.shape[1] == 2:
                cadence = px.scatter(cadence_df, x='dateTime', y='value', title='Cadence', template='plotly_dark', 
                                        color='value')
            
                return cadence
            
            else:
                
                return px.scatter(x=['Not available'], y=['Not available'], title='Cadence', template='plotly_dark')

@app.callback(
    [dash.dependencies.Output('graph6', 'figure'),
    dash.dependencies.Output('graph7', 'figure')],
    dash.dependencies.Input('drop_activities', 'value')
)

def update_heart_rate(activity):
    
    if activity is None:
        raise PreventUpdate
           
    else:

        filtered_df = df[df['startTime'] == activity]
        
        if filtered_df['samples.heartRate'].isnull().values.any():
            
            empty_h = px.scatter(x=['Not available'], y=['Not available'], title='Heart Rate', template='plotly_dark')
            empty_z = px.scatter(x=['Not available'], y=['Not available'], title='Heart Rate Zones', template='plotly_dark')
            
            return empty_h, empty_z 
        
        else:
            heart_rate_df = pd.json_normalize(data=filtered_df.iloc[0]['samples.heartRate'], max_level=1)
            
            if heart_rate_df.shape[1] == 2:
                heart_rate = px.scatter(heart_rate_df, x='dateTime', y='value', title='Heart Rate', template='plotly_dark', 
                                        color='value')
                
                ranges = [0, 99, 119, 139, 158, 178, 198, np.inf]
                groups = ['0-99bpm', '99-119bpm', '119-139', '139-158bpm', '158-178bpm', '178-198bpm', 'Above 198bpm']
                heart_rate_df['heartRateZones'] = pd.cut(heart_rate_df['value'], bins=ranges, labels=groups)
                zones_count = heart_rate_df.groupby('heartRateZones').count().reset_index()
                zones = px.bar(zones_count, x='heartRateZones', y='value', color='heartRateZones', title='Heart Rate Zones', template='plotly_dark')
                
                return heart_rate, zones
            
            else:
                
                empty_h = px.scatter(x=['Not available'], y=['Not available'], title='Heart Rate', template='plotly_dark')
                empty_z = px.scatter(x=['Not available'], y=['Not available'], title='Heart Rate Zones', template='plotly_dark')
                return empty_h, empty_z


# ---------------------------------------------
# app layout
app.layout = html.Div([
    html.H1(children='Polar Smart Watch - Sports and Fitness Data',
            style={
                'backgroundColor': colors['background'], 
                'color': colors['text'],
                'textAlign':'center',
                'fontSize':'7rem'
            }
    ),
    dcc.Tabs(id='tabs', value='tab1', children=[
        
        dcc.Tab(
            id='general_data', 
            label='TAB 1 - General Data', 
            value='tab1', 
            style={'backgroundColor': colors['background'], 
                   'color': colors['text']}
        ),
        
        dcc.Tab(
            id="activity_data", 
            label='TAB 2 - Sports and Activities Data', 
            value='tab2', 
            style={'backgroundColor': colors['background'], 
                   'color': colors['text']}
        ),
    
    ], style={'backgroundColor': colors['background'], 'color': colors['text']}),
    
    html.Div(id='content',
             children = tab1_layout, 
             style={'backgroundColor': colors['background'], 'color': colors['text']}
    ),
    
], style={'backgroundColor': colors['background'], 'color': colors['text']})

# -------------------
# tab callback

@app.callback(
    dash.dependencies.Output('content', 'children'),
    [dash.dependencies.Input('tabs', 'value')]
)
def render_content(tab):
    if tab == 'tab1':
        return tab1_layout
    elif tab == 'tab2':
        return tab2_layout


if __name__ == '__main__':
    app.run_server(debug=True)
