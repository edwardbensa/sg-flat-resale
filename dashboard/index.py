# index.py
from dash import dcc, html, Input, Output
from app import app
from pages import home, units_resold, median_price

# Sidebar layout
sidebar = html.Div([
    html.H2("Dashboard", style={'textAlign': 'center'}),
    html.Hr(),
    dcc.Link('Home', href='/', style={'display': 'block', 'margin': '10px'}),
    dcc.Link('Units Resold', href='/units-resold', style={'display': 'block', 'margin': '10px'}),
    dcc.Link('Median Price', href='/median-price', style={'display': 'block', 'margin': '10px'}),
], style={
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '200px',
    'padding': '20px',
    'background-color': '#f8f9fa',
    'font-family': 'Arial, sans-serif'
})

# Main content area
content = html.Div(id='page-content', style={'margin-left': '220px', 'padding': '20px'})

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    sidebar,
    content
])

# Routing logic
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/units-resold':
        return units_resold.layout
    elif pathname == '/median-price':
        return median_price.layout
    else:
        return home.layout

if __name__ == '__main__':
    app.run(debug=True)
