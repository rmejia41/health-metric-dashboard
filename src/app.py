# App with 2 dropdown, 2 plots and risk factor, regression button

from dash import Dash, dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

df = pd.read_csv('https://github.com/rmejia41/open_datasets/raw/main/dataset_.csv')
# Initialize the Dash ap
app = Dash(__name__, external_stylesheets=[dbc.themes.MORPH],  # LITERA, SANDSTONE, SPACELAB, SOLAR
           meta_tags=[{'name': 'viewport',
                       'content': 'width=device-width, initial-scale=1.0'}]
           )  # mobile functionality
server = app.server

def filtered_data_none(selected_data):
    return selected_data


app.layout = dbc.Container([

    dbc.Row(
        dbc.Col(html.H1('Health Dashboard',
                        className='text-center text-primary mb-4'),  # mb-4 is the spacing between titles
                width=12)
    ),

    dbc.Row(
        dbc.Col(html.H1('Clinical Outcomes and Risk Factors',
                        className='text-center text-primary mb-4'),
                width=12)
    ),

    dbc.Row([

        dbc.Col(['Select Health Metric',
                 dcc.Dropdown(
                     id='health-metric-dropdown',
                     value='BMI',
                     options=[
                         {'label': 'Body Mass Index', 'value': 'BMI'},
                         {'label': 'Clinical Systolic Blood Pressure', 'value': 'Clinic_SBP'},
                         {'label': 'Clinical Diastolic Blood Pressure', 'value': 'Clinic_DBP'},
                         {'label': 'Night Time Diastolic Blood Pressure', 'value': 'DBP_NT'},
                         {'label': 'Night Time Systolic Blood Pressure', 'value': 'SBP_NT'},
                         {'label': 'Pittsburgh Sleep Quality Index Global Score', 'value': 'PSQI_Global'},
                         {'label': 'Beck Depression Inventory Score', 'value': 'BDI_ImputedScore2'},
                         # Added Depression Scale
                         {'label': 'Age in Years', 'value': 'Age'}
                     ]
                 ),
                 html.Br(),
                 dcc.Graph(id='health-scatter-plot', figure={})
                 ], width={'size': 6, 'offset': 0, 'order': 1},
                # xs=12, sm=12, md=12, lg=5, xl=5 #depending on the screen size, you change the graph's size, small, medium
                ),

        dbc.Col(['Select Risk Factors',
                 dcc.Dropdown(
                     id='risk-dropdown',
                     value='Diabetes',
                     options=[
                         {'label': 'Diabetes', 'value': 'Diabetes'},
                         {'label': 'Current Smoking', 'value': 'CurrentSmoking'},
                         {'label': 'Ever Pregnant', 'value': 'EverPreg'},
                         {'label': 'Blood Pressure Diagnosis and History', 'value': 'AntiHTN'},
                         {'label': 'Parental Status', 'value': 'ParentalStatus'},
                         {'label': 'Partner Status', 'value': 'PartnerStatus'},
                         {'label': 'Financial Health:Net Worth', 'value': 'NetWorth'},
                         {'label': 'Income', 'value': 'Income'}
                     ]
                 ),
                 html.Br(),
                 dcc.Graph(id='risk-box-plot', figure={})
                 ], width={'size': 4, 'offset': 1, 'order': '2'},
                # xs=12, sm=12, md=12, lg=5, xl=5
                ),
    ], justify='start'),
    # order switched the order of graphics in the column components
    # justify moves horizontally from left to right: center, end, between, around

    dbc.Row([
        dbc.Col([
            dbc.Button('Show Risk', id='no-risk-button', n_clicks=0)
        ], width={'size': 4, 'offset': 3, 'order': '2'}),

        dbc.Col([
            html.Button('Show Regression Line', id='regression-button', n_clicks=0),
        ], width={'size': 3, 'offset': 2, 'order': '1'}),
    ]),
], fluid=False)


# Define the callback function
@app.callback(
    Output('health-scatter-plot', 'figure'),
    Output('risk-box-plot', 'figure'),
    [Input('health-metric-dropdown', 'value'),
     Input('risk-dropdown', 'value'),
     Input('no-risk-button', 'n_clicks'),
     Input('regression-button', 'n_clicks')]
)
def update_scatter_plot(selected_metric, selected_risk, no_risk_clicks, n_clicks):
    # Filter the data based on the selected risk factor
    filtered_data = df.copy()

    if selected_risk != 'None' and no_risk_clicks % 2 == 1:
        filtered_data = filtered_data[filtered_data[selected_risk] == 1]  # selects variables coded not in "1"

    # Create a scatter plot for the selected metric with color style based on "Current Smoking" using Plotly Express
    fig = px.scatter(
        filtered_data,
        x='Age',  # Use 'Age' as x values
        y=selected_metric,
        color='IntentionalExercise',
        color_continuous_scale='Cividis',  # You can choose a different color scale
        size_max=15,
        size='BMI',
        labels={'Age': 'Age in Years', 'BMI': 'Body Mass Index', 'IntentionalExercise': 'Intentional Exercise',
                selected_metric: selected_metric}
    )

    fig.update_layout(
        xaxis_title='Age in Years',
        yaxis_title=selected_metric,
        showlegend=False
    )

    # Box-Plot
    box_plot_fig = px.box(
        filtered_data,
        x=selected_risk,
        y=selected_metric,
        title=f'{selected_risk} by {selected_metric}',
        labels={selected_risk: 'Risk Factor', 'selected_metric': f'{selected_metric}'},
    )

    # update teh y-axis title for selected health metric
    box_plot_fig.update_yaxes(title=f'{selected_metric}')

    if n_clicks and n_clicks % 2 == 1:
        # calculate the regression line
        x = filtered_data['Age']
        y = filtered_data[selected_metric]
        m, b = np.polyfit(x, y, 1)
        regression_line = m * x + b
        fig.add_trace(go.Scatter(x=x, y=regression_line, mode='lines', name='Regression Line', line=dict(color='red')))

    return fig, box_plot_fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=False, port=3000)