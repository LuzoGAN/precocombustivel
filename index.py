import dash_bootstrap_components
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from app import *
from dash_bootstrap_templates import ThemeSwitchAIO

#Estilos
url_theme1 = dbc.themes.VAPOR
url_theme2 = dbc.themes.FLATLY
template_theme1 = 'vapor'
template_theme2 = 'flatly'

#Lendo dados
df = pd.read_csv('data_gas.csv')
state_options = [{'label': x, 'value': x} for x in df['ESTADO'].unique()]

#Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            ThemeSwitchAIO(aio_id='theme', themes=[url_theme1,url_theme2]),
            html.H3('Preço x estado'),
            dcc.Dropdown(
                id='estados',
                value=[state['label'] for state in state_options[:3]],
                multi=True,
                options=state_options
            ),
            dcc.Graph(id='line_graph')
        ])
    ]),
    dbc.Row([
        dbc.Col([
            #drop 1
            dcc.Dropdown(
                id='estado1',
                value=state_options[0]['label'],
                options=state_options
            )
        ], sm=12, md=6),
        dbc.Col([
            #drop 2
            dcc.Dropdown(
                id='estado2',
                value=state_options[1]['label'],
                options=state_options
            )
        ],sm=12 , md=6),
        dbc.Col([
            dcc.Graph(id='indicator1')
        ]),
        dbc.Col([
            dcc.Graph(id='indicator2')
        ])
    ])
])

#callbacks
@app.callback(
    Output('line_graph', 'figure'),
    Input('estados', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)
def line(estados, toogle):
    template = template_theme1 if toogle else template_theme2

    df_data = df.copy(deep=True)
    mask = df_data['ESTADO'].isin(estados)

    fig = px.line(df_data[mask], x='DATA INICIAL', y='PREÇO MÉDIO REVENDA', color='ESTADO', template=template)

    return fig


# Indicadores
@app.callback(
    Output('indicator1', 'figure'),
    Output('indicator2', 'figure'),
    Input('estado1', 'value'),
    Input('estado2', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)
def indicators(estado1, estado2, toogle):
    template = template_theme1 if toogle else template_theme2

    df_date = df.copy(deep=True)
    data_estado1 = df_date[df_date['ESTADO'].isin([estado1])]
    data_estado2 = df_date[df_date['ESTADO'].isin([estado2])]

    initial_date = str(int(df_date['PREÇO MÍNIMO REVENDA'].min()) -1 )
    final_date = df_date['PREÇO MÁXIMO REVENDA'].max()

    interable = [(estado1, data_estado1), (estado2, data_estado2)]
    indicators = []

    for estado, data in interable:
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode='number+delta',
            title={'text': f"<span>{estado}</span><br><span style='font-size>0.7em'>{initial_date} - {final_date}</span>"},
            value=data.at[data.index[-1], 'PREÇO MÉDIO REVENDA'],
            number={'prefix': 'R$', 'valueformat': '.2f'},
            delta={'relative': True, 'valueformat': '.1%', 'reference': data.at[data.index[0], 'PREÇO MÉDIO REVENDA']}
        ))

        fig.update_layout(template=template)
        indicators.append(fig)
    return indicators

#Iniciar Servidor
if __name__ == '__main__':
    app.run_server(debug=False)