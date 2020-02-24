import dash
import dash_core_components as dcc
import dash_html_components as html
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
        data = {'title':'please make a selection', 'release_date':' ', 'overview':' '}
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
        data = 'your text will be displayed here after you press the button'
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
