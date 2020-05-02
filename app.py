import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from dash.dependencies import Input, Output
import pandas as pd
import altair as alt
from vega_datasets import data

app = dash.Dash(__name__, assets_folder='assets', external_stylesheets=[dbc.themes.UNITED])
server = app.server

app.title = 'Flavortown'

# Import data
df_choro = pd.read_csv('data/df_choropleth.csv')
df_table = pd.read_csv('data/df_yelp.csv')

# Create list of regions for dropdown menu
loc_list = []
for loc in df_table['state'].unique():
    loc_list.append({'label': loc, 'value': loc})

# Sort regions in alphabetical order
loc_list = sorted(loc_list, key = lambda i: i['label']) 

# Create list of seasons for dropdown menu
season_list = []
for s in df_table['season'].unique():
   season_list.append({'label': s, 'value': s})

states = alt.topo_feature(data.us_10m.url, feature='states')

def make_choropleth():

   """Draw a map of featured restaurants."""

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
            .mark_circle(size=15, color='red')
            .encode(
               longitude='longitude:Q',
               latitude='latitude:Q',
               tooltip=['location', 'place(s) visited']
            ).project('albersUsa')
   )
   
   choropleth = background + locations

   return choropleth

def make_table(region=['California', 'Texas', 'Florida'], season=[2, 14, 29]):
   
   """Create a table of featured restaurants."""

   if len(region) == 0:
      region = df_table['state'].unique()
   if len(season) == 0:
      season = df_table['season'].unique()
      
   table_state = df_table[df_table['state'].isin(region)] 
   table_season = df_table[df_table['season'].isin(season)]

   result = table_state.merge(table_season, how='inner')

   return result

# Create header
header = html.Div(
   dbc.Row(
      [
         dbc.Col(
            html.Div([
               html.H1('A Visual Guide to Flavortown'),
               html.P("Diners, Drive-Ins and Dives is a popular TV show on Food Network hosted by celebrity chef Guy Fieri. Now on its 30th season, Diners, Drive-Ins and Dives showcases independent restaurants serving up delicious comfort food across North America."),
               html.P("This dashboard features an interactive map that allows you to discover the cities and restaurants visited by Fieri. You can also use the dropdown menus to filter the featured restaurants by season and/or location."),
               ]
            ),
            width={'size': 5, 'offset': 1}
         ),
         dbc.Col(
            html.Div(
               html.Img(src='https://chapspitbeef.com/wp-content/uploads/2017/11/diner-driveins-dives-logo.jpeg', width='60%')), 
               width=6),
      ]
   )
) 

# Create content
content = html.Div(
   [
      dbc.Row(
         dbc.Col(
            html.Iframe(
               sandbox='allow-scripts',
               id='choropleth',
               height='600',
               width='1100',
               style={'border-width': '0px'},
               srcDoc=make_choropleth().to_html()
            ),
            width={'size': 6, 'offset': 3}
         ),
      ),
      dbc.Row(
         [
            dbc.Col(
               [
                  dbc.Row(
                     [
                        html.H6('Select region:'),
                        dcc.Dropdown(
                           id='region',
                           options=loc_list,
                           value=['California', 'Texas', 'Florida'],
                           multi=True,
                           style={'width': '80%'}
                        ),
                        html.H6('Select season:'),
                        dcc.Dropdown(
                           id='season',
                           options=season_list,
                           value=[2, 14, 29],
                           multi=True,
                           style={'width': '80%'}
                        ),
                     ]
                  ),
               ],
               width={'size': 3, 'offset': 1}
            ),
            dbc.Col(
               dash_table.DataTable(
                  id='table',
                  data=df_table.to_dict('records'),
                  columns=[{'id': c, 'name': c} for c in df_table.columns],
                  fixed_rows={'headers': True},
                  page_size=20,
                  style_table={'height': '300px', 'overflowY': 'auto'},
                  style_cell={'whiteSpace': 'normal', 'height': 'auto',},
                  style_cell_conditional=[
                     {'if': {'column_id': 'season'}, 'width': '7.5%'},
                     {'if': {'column_id': 'episode'}, 'width': '7.5%'},
                     {'if': {'column_id': 'rating'}, 'width': '7.5%'},
                     {'if': {'column_id': 'price'}, 'width': '7.5%'},
                  ]
               ),
               width={'size': 7}
            ),
         ]
      ),
   ]
)

# Create footer
footer = html.Div(
   [
      dbc.Row(
         dbc.Col(
            html.H6('Data:'),
            width={'offset': 1}
         )
      ),
      dbc.Row(
         dbc.Col(
             html.A('List of Diners, Drive-Ins and Dives episodes', href='https://en.wikipedia.org/wiki/List_of_Diners,_Drive-Ins_and_Dives_episodes'),
             width={'offset': 1}
         )
      ),
      dbc.Row(
         dbc.Col(
            html.H6('Image:'),
            width={'offset': 1}
         )
      ),
      dbc.Row(
         dbc.Col(
            html.A('Chaps Pit Beef', href='https://chapspitbeef.com/wp-content/uploads/2017/11/diner-driveins-dives-logo.jpeg'),
            width={'offset': 1}
         )
      ),
   ]
)

app.layout = html.Div([
   header,
   content,
   footer,
])

@app.callback(
   dash.dependencies.Output(component_id='table', component_property='data'),
   [
      dash.dependencies.Input(component_id='region', component_property='value'),
      dash.dependencies.Input(component_id='season', component_property='value')
   ]
)

def update_table(region, season):

   """Given user-specified regions and seasons, update the table of featured restaurants."""

   new_table = make_table(region, season).to_dict('records')

   return new_table

if __name__ == '__main__':
    app.run_server(debug=True)