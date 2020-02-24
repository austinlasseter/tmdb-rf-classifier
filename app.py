import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import plotly.graph_objs as go
import pandas as pd
import random
import pickle
import sklearn

from helpers.key_finder import api_key
from helpers.api_call import *


########### Define a few variables ######

tabtitle = 'Genre Game'
sourceurl = 'https://www.kaggle.com/jrobischon/wikipedia-movie-plots'
sourceurl2 = 'https://www.themoviedb.org/'
githublink = 'https://github.com/austinlasseter/movie_genres'

# pickled vectorizer
file = open('analysis/vectorizer.pkl', 'rb')
vectorizer=pickle.load(file)
file.close()

# open the pickled RF model file
file = open(f'analysis/trained_rf_model.pkl', 'rb')
rf_model_pickled=pickle.load(file)
file.close()

######## Define the figure

top20=pd.read_csv('analysis/top20.csv')

# Define the color palette (19 colors).
Viridis= ['#440154', '#48186a', '#472d7b', '#424086', '#3b528b', '#33638d', '#2c728e', '#26828e', '#21918c', '#1fa088',
          '#28ae80', '#3fbc73', '#5ec962', '#84d44b', '#84d44b', '#addc30','#d8e219', '#fde725',  '#fde725']

mydata = [go.Bar(
    x=top20['feature'],
    y=top20['importance'],
    marker=dict(color=Viridis[::-1])
)]

mylayout = go.Layout(
    title='What makes it a horror film?',
    xaxis = dict(title = 'Words most associated with being a horror movie'),
    yaxis = dict(title = 'Feature Importance'),

)
fig = go.Figure(data=mydata, layout=mylayout)

## Confusion Matrix
cm = pd.read_csv('analysis/conf_matrix.csv')

########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

########### Layout

app.layout = html.Div(children=[
    dcc.Store(id='tmdb-store', storage_type='session'),
    dcc.Store(id='summary-store', storage_type='session'),
    html.Div([
        html.H4(['Genre Game']),
        html.Div('Press the button to pick a movie'),
        html.Button(id='bam-button', n_clicks=0, children='BAM!'),
        html.Div(id='movie-title', children=[]),
        html.Div(id='movie-release', children=[]),
        html.Div(id='movie-overview', children=[]),
        html.Br(),
        html.Div('Enter the movie summary below (try adding a few words to change it up!)'),
        dcc.Input(
            id='summary-input',
            type='text',
            size='100',
            placeholder='Type or paste your movie summary here',
        ),
        html.Button(id='biff-button', n_clicks=0, children='BIFF!'),
        html.Div(id='summary-output', children='Press the button!'),
        html.Br(),
        html.Div(id='prediction-div'),
        dcc.Graph(id='top20', figure=fig),
        html.Div([
            html.Div(id='cm', children=['Confusion Matrix: Random Forest Classifier']),
            dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in cm.columns],
                data=cm.to_dict('records'),
                style_header={'backgroundColor': 'rgb(30, 30, 30)'},
                style_cell={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white'
                }),
            ], className='six columns'),
        html.Div([' '], className='six columns'),
    ], className='twelve columns'),


        # Output
    html.Div([
        # Footer
        html.Br(),
        html.A('Code on Github', href=githublink, target="_blank"),
        html.Br(),
        html.A("Data Source: Kaggle", href=sourceurl, target="_blank"),
        html.Br(),
        html.A("Data Source: TMDB", href=sourceurl2, target="_blank"),
    ], className='twelve columns'),



    ]
)

########## Callbacks

# TMDB API call
@app.callback(Output('tmdb-store', 'data'),
              [Input('bam-button', 'n_clicks')],
              [State('tmdb-store', 'data')])
def on_click(n_clicks, data):
    if n_clicks is None:
        raise PreventUpdate
    elif n_clicks==0:
        data = {'title':' ', 'release_date':' ', 'overview':' '}
    elif n_clicks>0:
        data = api_pull(random.choice(ids_list))
    return data

@app.callback([Output('movie-title', 'children'),
                Output('movie-release', 'children'),
                Output('movie-overview', 'children'),
                ],
              [Input('tmdb-store', 'modified_timestamp')],
              [State('tmdb-store', 'data')])
def on_data(ts, data):
    if ts is None:
        raise PreventUpdate
    else:
        return data['title'], data['release_date'], data['overview']

# User writes their own summary

@app.callback(Output('summary-store', 'data'),
              [Input('biff-button', 'n_clicks')],
              [State('summary-input', 'value')]
              )
def on_click(n_clicks, value):
    if n_clicks is None:
        raise PreventUpdate
    elif n_clicks==0:
        data = ' '
    elif n_clicks>0:
        data = str(value)
    return data

@app.callback([Output('summary-output', 'children'),
               Output('prediction-div', 'children')],
              [Input('summary-store', 'modified_timestamp')],
              [State('summary-store', 'data')])
def on_data(ts, data):
    if ts is None:
        raise PreventUpdate
    else:
        vectorized_text=vectorizer.transform([data])
        probability=100*rf_model_pickled.predict_proba(vectorized_text)[:,1]
        return data, str(f'Probability of being a horror movie: {probability[0]}%')



############ Deploy
if __name__ == '__main__':
    app.run_server(debug=True)
