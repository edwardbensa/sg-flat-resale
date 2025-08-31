from dash import html, dcc
from src.utils.plotting import catplots
from dashboard.utils.data import df_p, x_vars

fig = catplots(df_p, x_vars, 'flat_type', 'Median Flat Resale Price By Flat Type (Inflation Adjusted)', 'median')

# pages/home.py
layout = html.Div([
    html.H1("Median Price"),
    html.P("Median flat resale price by feature."),
    dcc.Graph(figure=fig)
])
