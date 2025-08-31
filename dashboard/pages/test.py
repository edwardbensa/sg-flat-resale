# Import packages
from dash import Dash, html, dash_table, dcc
import pandas as pd
import plotly.express as px

from src.utils.plotting import catplots
from dashboard.utils.data import df_p, x_vars

fig_1 = catplots(df_p, x_vars, 'flat_type', 'Units Resold By Flat Type', 'count')
fig_2 = catplots(df_p, x_vars, 'years_leased_binned', 'Units Resold By Years Leased', 'count')

# Incorporate data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

# Initialize the app
app = Dash()

# App layout
app.layout = [
    html.Div(children='My First App with Data and a Graph'),
    fig_1,
    fig_2,
]

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
