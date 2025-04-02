# https://a7-1.onrender.com
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import pycountry

# Step 1: Create the dataset
def create_dataset():
    url = 'https://en.wikipedia.org/wiki/List_of_FIFA_World_Cup_finals'
    tables = pd.read_html(url)
    
    for i, table in enumerate(tables):
        if 'Year' in str(table.columns):
            df = table
            break
    
    df.columns = [str(col).strip() for col in df.columns]
    df['Winners'] = df['Winners'].astype(str).apply(lambda x: 'Germany' if x in ['West Germany', 'Germany'] else x)
    df['Winners'] = df['Winners'].replace('England', 'United Kingdom')
    df['Runners-up'] = df['Runners-up'].astype(str).apply(lambda x: 'Germany' if x in ['West Germany', 'Germany'] else x)
    
    return df

df = create_dataset()

win_counts = df['Winners'].value_counts().reset_index()
win_counts.columns = ['Country', 'Wins']

def get_iso_alpha3(country):
    try:
        return pycountry.countries.get(name=country).alpha_3
    except:
        if country == 'United Kingdom':
            return 'GBR'
        return None

win_counts['ISO'] = win_counts['Country'].apply(get_iso_alpha3)
win_counts = win_counts.dropna(subset=['ISO'])

app = dash.Dash()
server = app.server

app.layout = html.Div([
    html.H1('FIFA World Cup Winners Dashboard', style={'textAlign': 'center'}),
    
    # Part a: All winning countries
    html.Div([
        html.H2('All-Time World Cup Winners', style={'textAlign': 'center'}),
        html.Ul([
            html.Li(f"{country} ({wins} wins)") 
            for country, wins in zip(win_counts['Country'], win_counts['Wins'])
        ], style={'width': '50%', 'margin': 'auto'})
    ]),
    
    # Choropleth map
    html.Div([
        html.H2('World Cup Wins by Country', style={'textAlign': 'center'}),
        dcc.Graph(
            figure=px.choropleth(
                win_counts,
                locations='ISO',
                color='Wins',
                hover_name='Country',
                color_continuous_scale='Viridis',
                title='World Cup Victories'
            ).update_layout(
                geo=dict(showframe=False, showcoastlines=True),
                width=1000,
                height=600
            )
        )
    ]),
    
    # Part b: Country wins selector
    html.Div([
        html.H2('Number of Wins by Country', style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='country-select',
            options=[{'label': c, 'value': c} for c in sorted(win_counts['Country'])],
            value=win_counts['Country'].iloc[0],
            style={'width': '50%', 'margin': 'auto'}
        ),
        html.Div(id='win-count', style={'textAlign': 'center', 'margin': '20px'})
    ]),
    
    # Part c: Year selection
    html.Div([
        html.H2('Final Match Details by Year', style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='year-select',
            options=[{'label': str(y), 'value': y} for y in sorted(df['Year'])],
            value=df['Year'].iloc[-1],
            style={'width': '50%', 'margin': 'auto'}
        ),
        html.Div(id='year-details', style={'textAlign': 'center', 'margin': '20px'})
    ])
], style={'padding': '20px'})

@app.callback(
    Output('win-count', 'children'),
    Input('country-select', 'value')
)
def update_win_count(country):
    count = win_counts[win_counts['Country'] == country]['Wins'].values[0]
    return f'{country} has won the World Cup {count} time{"s" if count > 1 else ""}'

@app.callback(
    Output('year-details', 'children'),
    Input('year-select', 'value')
)
def update_year_details(year):
    match_data = df[df['Year'] == year].iloc[0]
    return html.Div([
        html.H3(f'World Cup {year}'),
        html.P(f'Winner: {match_data["Winners"]}'),
        html.P(f'Runner-up: {match_data["Runners-up"]}')
    ])

if __name__ == '__main__':
    app.run(debug=True)
