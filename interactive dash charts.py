# -*- coding: utf-8 -*-
"""
Created on Sat Apr 13 13:25:23 2019

@author: jingyi
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Output, Input
import pandas as pd

#%% initialize dash and import data
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv(
    'https://gist.githubusercontent.com/chriddyp/'
    'cb5392c35661370d95f300086accea51/raw/'
    '8e0768211f6b747c0db42a9ce9a0937dafcbd8b2/'
    'indicators.csv')

indicators = df['Indicator Name'].unique()

#%% layout and elements

# 2 dropdowns and radios
dropdown_radio = html.Div([

        html.Div([
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in indicators],
                value='Fertility rate, total (births per woman)'
            ),
            dcc.RadioItems(
                id='crossfilter-xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in indicators],
                value='Life expectancy at birth, total (years)'
            ),
            dcc.RadioItems(
                id='crossfilter-yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    })

# dash layout
app.layout = html.Div([
    html.H3('Dash interactive visualization web APP'),
    dcc.Markdown("Try to hover around the data points in the scatter plot and see the change of time series on the right."),
    dropdown_radio,
    # scatter graph
    html.Div([
        dcc.Graph(id='indicator_scatterplot',
                  hoverData={'points': [{'customdata':'Switzerland'}]})],
          style = {'width': '49%','display':'inline-block','padding':'0 20'}),
    # time series graph
    html.Div([
        dcc.Graph(id='x-time-series'),
        dcc.Graph(id='y-time-series')],
        style = {'width': '48%','display':'inline-block'}),
    # slider to control time in scatter plot
    html.Div([
        dcc.Slider(
            id='year-slider',
            min=df.Year.min(),
            max=df.Year.max(),
            value=df.Year.max(),
            marks={str(year): str(year) for year in df.Year.unique()})],
            style={'width': '45%','padding':'20px 20px 20px 20px'})
    ])
        
#%% callback functions

# update scatter graph with year
@app.callback(
    Output('indicator_scatterplot','figure'),
    [Input('crossfilter-xaxis-column','value'),
     Input('crossfilter-yaxis-column','value'),
     Input('crossfilter-xaxis-type','value'),
     Input('crossfilter-yaxis-type','value'),
     Input('year-slider','value')]
    )
def update_scattergraph(xaxis_column,yaxis_column,xaxis_type,yaxis_type,year):
    df2 = df[df.Year == year]
    return {
        'data':[go.Scatter(
            x=df2[df2['Indicator Name']==xaxis_column]['Value'],
            y=df2[df2['Indicator Name']==yaxis_column]['Value'],
            text=df2[df2['Indicator Name']==yaxis_column]['Country Name'],
            customdata=df2[df2['Indicator Name']==yaxis_column]['Country Name'],
            mode='markers',
            marker={
                'size':15,
                'opacity':0.7,
                'line':{'width':0.5, 'color':'white'}})],
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column,
                'type': 'linear' if xaxis_type=='Linear' else 'log'
            },
            yaxis={
                'title': yaxis_column,
                'type': 'linear' if yaxis_type=='Linear' else 'log'
            },
            margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
            height=450,
            hovermode='closest'
        )
    }


def create_ts(df2,axis_type,title,color):
    return{
        'data':[
            go.Scatter(x=df2['Year'],y=df2['Value'],
                       mode='lines+markers',
                       marker=dict(color=color),
                       line=dict(color=color))        
        ],
        'layout': go.Layout(
            height=225,
            margin={'l': 20, 'b': 30, 'r': 10, 't': 10},
            annotations=[{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
            yaxis= {'type': 'linear' if axis_type == 'Linear' else 'log'},
            xaxis= {'showgrid': False}
        )
    }    


# update x timeseries
@app.callback(
    Output('x-time-series','figure'),
    [Input('indicator_scatterplot','hoverData'),
     Input('crossfilter-xaxis-column','value'),
     Input('crossfilter-xaxis-type','value')])
def update_xts(hoverData,xaxis_column,xaxis_type):
    country = hoverData['points'][0]['customdata']
    df2=df[df['Country Name'] == country]
    df2=df2[df2['Indicator Name'] == xaxis_column]
    title='<b>{}</b><br>{}'.format(country, xaxis_column)
    return create_ts(df2,xaxis_type,title,'rgb(8,81,156)')

# update y timeseries
@app.callback(
    Output('y-time-series','figure'),
    [Input('indicator_scatterplot','hoverData'),
     Input('crossfilter-yaxis-column','value'),
     Input('crossfilter-yaxis-type','value')])
def update_yts(hoverData,yaxis_column,yaxis_type):
    country = hoverData['points'][0]['customdata']
    df2=df[df['Country Name'] == country]
    df2=df2[df2['Indicator Name'] == yaxis_column]
    return create_ts(df2,yaxis_type,yaxis_column,'rgb(107,174,214)')
        

#%% execute the app
if __name__ == '__main__':
    app.run_server(debug=True)