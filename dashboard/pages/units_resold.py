from dash import html, dcc
from src.utils.plotting import catplots
from dashboard.utils.data import df_p, x_vars

fig_1 = catplots(df_p, x_vars, 'flat_type', 'Units Resold By Flat Type', 'count')
fig_2 = catplots(df_p, x_vars, 'years_leased_binned', 'Units Resold By Years Leased', 'count')

layout = html.Div([
    html.H1("Units Resold"),
    html.P("Number of units resold by feature."),
    html.H3("By Flat Type"),
    dcc.Graph(figure=fig_1),
    html.H3("By Years Leased"),
    dcc.Graph(figure=fig_2)
])
