import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import pandas as pd
import altair as alt
from vega_datasets import data

app = dash.Dash(__name__, assets_folder='assets')
server = app.server

app.title = 'Visual guide to Flavortown'

# Import data
df_choro = pd.read_csv('data/df_choropleth.csv')
df_table = pd.read_csv('data/df_coordinates.csv')

# Remove unused columns
df_table = df_table.drop(columns=['title', 'air_date', 'latitude', 'longitude'])

states = alt.topo_feature(data.us_10m.url, feature='states')

def make_choropleth():

   """Make a table of places Guy Fieri has visited."""

   background = (alt
               .Chart(states)
               .mark_geoshape(
                     fill='lightgray',
                     stroke='white'
               ).properties(
                     width=1000,
                     height=500
               ).project('albersUsa')
   )

   locations = (alt
            .Chart(df_choro)
            .mark_circle(size=10, color='red')
            .encode(
               longitude='longitude:Q',
               latitude='latitude:Q',
               tooltip=['location', 'place(s) visited']
            ).project('albersUsa')
   )
   
   choropleth = background + locations

   return choropleth

app.layout = html.Div([
   html.H1('A visual guide to Flavortown'),
   html.Iframe(
        sandbox='allow-scripts',
        id='choropleth',
        height='600',
        width='1100',
        style={'border-width': '0px'},
        srcDoc=make_choropleth().to_html()
   ),
   dash_table.DataTable(
      data=df_table.to_dict('records'),
      columns=[{'id': c, 'name': c} for c in df_table.columns],
      style_table={
         'maxHeight': '300px',
         'overflowX': 'scroll',
         'overflowY': 'scroll'
      },
      style_cell={
        'height': '20px',
        'minWidth': '0px', 'maxWidth': '100px',
        'whiteSpace': 'normal'
      }
   ),
])

if __name__ == '__main__':
    app.run_server(debug=True)