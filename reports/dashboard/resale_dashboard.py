import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import geopandas as gpd

from src.config import PROCESSED_DATA_DIR, EXTERNAL_DATA_DIR

# Import geojson file
town_geo = gpd.read_file(EXTERNAL_DATA_DIR / 'district_and_planning_area.geojson')

# Import and load cleaned data
filename = PROCESSED_DATA_DIR / 'ResaleFlatPrices-Processed.csv'
df = pd.read_csv(PROCESSED_DATA_DIR / filename)
df['date'] = pd.to_datetime(df['date'])

def bin_numbers(number, start, step):
    start_number = start
    interval = step
    interval_number = start_number + interval - 1
    addend = interval * ((number - start_number) // interval)
    return f"{start_number + addend}-{interval_number + addend}"

# Copy main dataframe for plotting purposes
df_p = df.copy()
df_p['year_binned'] = df_p['year'].apply(lambda a: bin_numbers(a, 1990, 10))
df_p['lease_year_binned'] = df_p['lease_year'].apply(lambda a: bin_numbers(a, 1960, 10))
df_p['years_leased_binned'] = df_p['years_leased'].apply(lambda a: bin_numbers(a, 0, 10))
df_p['start_floor_binned'] = df_p['start_floor'].apply(lambda a: bin_numbers(a, 1, 10))
df_p['quarter'] = df_p['month'].apply(lambda a: bin_numbers(a, 1, 3))
df_p['quarter'] = df_p['quarter'].replace({'1-3': 'Q1', '4-6': 'Q2', '7-9': 'Q3', '10-12': 'Q4',})


import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the available options for Units Resold
UNITS_GROUP_OPTIONS = [
    {'label': 'Flat Type', 'value': 'flat_type'},
    {'label': 'Years Leased', 'value': 'years_leased_binned'},
    {'label': 'Lease Year', 'value': 'lease_year_binned'},
    {'label': 'Quarter', 'value': 'quarter'}
]

# Define the available options for Mean Price
PRICE_GROUP_OPTIONS = [
    {'label': 'Flat Type', 'value': 'flat_type'},
    {'label': 'Starting Floor', 'value': 'start_floor_binned'},
    {'label': 'Region', 'value': 'region'}
]

X_AXIS_OPTIONS = [
    {'label': 'Year', 'value': 'year'},
    {'label': 'Lease Year', 'value': 'lease_year'},
    {'label': 'Years Leased', 'value': 'years_leased'},
    {'label': 'Month', 'value': 'month'}
]

# Sidebar style
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "backgroundColor": "#f8f9fa",
    "borderRight": "1px solid #dee2e6"
}

# Main content style
CONTENT_STYLE = {
    "marginLeft": "18rem",
    "marginRight": "2rem",
    "padding": "2rem 1rem",
}

# Navigation link style
NAV_LINK_STYLE = {
    "display": "block",
    "padding": "0.5rem 1rem",
    "margin": "0.25rem 0",
    "textDecoration": "none",
    "color": "#495057",
    "borderRadius": "0.25rem",
    "cursor": "pointer"
}

NAV_LINK_ACTIVE_STYLE = {
    **NAV_LINK_STYLE,
    "backgroundColor": "#007bff",
    "color": "white"
}

# Sidebar component
sidebar = html.Div([
    html.H2("Dashboard", className="display-4", style={"fontSize": "1.5rem", "marginBottom": "1rem"}),
    html.Hr(),
    html.P("Navigation", className="lead", style={"fontSize": "1rem", "marginBottom": "1rem"}),
    html.Div([
        html.A("Units Resold", id="units-link", style=NAV_LINK_ACTIVE_STYLE),
        html.A("Mean Resale Price", id="price-link", style=NAV_LINK_STYLE),
    ], id="nav-links")
], style=SIDEBAR_STYLE)

# Main content area
content = html.Div(id="page-content", style=CONTENT_STYLE)

# App layout
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    sidebar,
    content
], style={'fontFamily': 'Arial, sans-serif'})

# Callback to update page content and navigation styling
@callback(
    [Output("page-content", "children"),
     Output("units-link", "style"),
     Output("price-link", "style")],
    [Input("url", "pathname"),
     Input("units-link", "n_clicks"),
     Input("price-link", "n_clicks")]
)
def display_page(pathname, units_clicks, price_clicks):
    # Determine which page to show
    if pathname == "/price" or (price_clicks and price_clicks > 0):
        return price_layout, NAV_LINK_STYLE, NAV_LINK_ACTIVE_STYLE
    else:
        return units_layout, NAV_LINK_ACTIVE_STYLE, NAV_LINK_STYLE

# Units Resold page layout
units_layout = html.Div([
    html.H1("Units Resold Dashboard", style={'textAlign': 'center', 'marginBottom': 30}),
    
    html.Div([
        html.Div([
            html.Label("Select Grouping Variable:", style={'fontWeight': 'bold', 'marginBottom': 10}),
            dcc.Dropdown(
                id='units-group-dropdown',
                options=UNITS_GROUP_OPTIONS,
                value='flat_type',
                style={'width': '100%'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%'}),
        
        html.Div([
            html.Label("Select X-axis Variable:", style={'fontWeight': 'bold', 'marginBottom': 10}),
            dcc.Dropdown(
                id='units-x-axis-dropdown',
                options=X_AXIS_OPTIONS,
                value='year',
                style={'width': '100%'}
            )
        ], style={'width': '48%', 'display': 'inline-block'})
    ], style={'marginBottom': 30}),
    
    dcc.Graph(id='units-resold-graph', style={'height': '70vh'})
])

# Mean Price page layout
price_layout = html.Div([
    html.H1("Mean Resale Price Dashboard", style={'textAlign': 'center', 'marginBottom': 30}),
    
    html.Div([
        html.Div([
            html.Label("Select Grouping Variable:", style={'fontWeight': 'bold', 'marginBottom': 10}),
            dcc.Dropdown(
                id='price-group-dropdown',
                options=PRICE_GROUP_OPTIONS,
                value='flat_type',
                style={'width': '100%'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%'}),
        
        html.Div([
            html.Label("Select X-axis Variable:", style={'fontWeight': 'bold', 'marginBottom': 10}),
            dcc.Dropdown(
                id='price-x-axis-dropdown',
                options=X_AXIS_OPTIONS,
                value='year',
                style={'width': '100%'}
            )
        ], style={'width': '48%', 'display': 'inline-block'})
    ], style={'marginBottom': 30}),
    
    dcc.Graph(id='mean-price-graph', style={'height': '70vh'})
])

# Callback for Units Resold graph
@callback(
    Output('units-resold-graph', 'figure'),
    [Input('units-group-dropdown', 'value'),
     Input('units-x-axis-dropdown', 'value')]
)
def update_units_graph(group_var, x_var):
    # Create subplot figure
    fig = make_subplots(
        rows=2, cols=1, 
        row_heights=[2, 0.5],
        subplot_titles=[f'Units Resold by {group_var.replace("_", " ").title()}', 'Total Units Resold'],
        vertical_spacing=0.1
    )
    
    # Group data by x_var and group_var
    df_plot = df_p.groupby([x_var, group_var]).size().reset_index(name='units_resold')
    
    # Add traces for each group
    for g in sorted(df_plot[group_var].unique()):
        df_g = df_plot[df_plot[group_var] == g]
        fig.add_trace(go.Scatter(
            x=df_g[x_var],
            y=df_g['units_resold'],
            mode='lines+markers',
            name=str(g),
            line=dict(width=2),
            marker=dict(size=4)
        ), row=1, col=1)
    
    # Add total units resold trace
    df_plot_all = df_p.groupby(x_var).size().reset_index(name='units_resold')
    fig.add_trace(go.Scatter(
        x=df_plot_all[x_var],
        y=df_plot_all['units_resold'],
        mode='lines+markers',
        name='Total',
        line=dict(width=3, color='black'),
        marker=dict(size=6),
        showlegend=False
    ), row=2, col=1)
    
    # Update layout
    fig.update_layout(
        margin=dict(l=50, r=50, t=80, b=50),
        hovermode='x unified',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.95,
            xanchor="left",
            x=1.02
        )
    )
    
    # Update axes labels
    fig.update_xaxes(title_text=x_var.replace('_', ' ').title(), row=1, col=1)
    fig.update_xaxes(title_text=x_var.replace('_', ' ').title(), row=2, col=1)
    fig.update_yaxes(title_text='Units Resold', row=1, col=1)
    fig.update_yaxes(title_text='Total Units Resold', row=2, col=1)
    
    return fig

# Callback for Mean Price graph
@callback(
    Output('mean-price-graph', 'figure'),
    [Input('price-group-dropdown', 'value'),
     Input('price-x-axis-dropdown', 'value')]
)
def update_price_graph(group_var, x_var):
    # Create subplot figure
    fig = make_subplots(
        rows=2, cols=1, 
        row_heights=[2, 0.5],
        subplot_titles=[f'Mean Resale Price by {group_var.replace("_", " ").title()}', 'Overall Mean Price'],
        vertical_spacing=0.1
    )
    
    # Group data by x_var and group_var
    df_plot = df_p.groupby([x_var, group_var])['infl_adj_price'].mean().reset_index()
    
    # Add traces for each group
    for g in sorted(df_plot[group_var].unique()):
        df_g = df_plot[df_plot[group_var] == g]
        fig.add_trace(go.Scatter(
            x=df_g[x_var],
            y=df_g['infl_adj_price'],
            mode='lines+markers',
            name=str(g),
            line=dict(width=2),
            marker=dict(size=4)
        ), row=1, col=1)
    
    # Add overall mean price trace
    df_plot_all = df_p.groupby(x_var)['infl_adj_price'].mean().reset_index()
    fig.add_trace(go.Scatter(
        x=df_plot_all[x_var],
        y=df_plot_all['infl_adj_price'],
        mode='lines+markers',
        name='Overall Mean',
        line=dict(width=3, color='black'),
        marker=dict(size=6),
        showlegend=False
    ), row=2, col=1)
    
    # Update layout
    fig.update_layout(
        margin=dict(l=50, r=50, t=80, b=50),
        hovermode='x unified',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.95,
            xanchor="left",
            x=1.02
        )
    )
    
    # Update axes labels
    fig.update_xaxes(title_text=x_var.replace('_', ' ').title(), row=1, col=1)
    fig.update_xaxes(title_text=x_var.replace('_', ' ').title(), row=2, col=1)
    fig.update_yaxes(title_text='Mean Price (Inflation Adjusted)', row=1, col=1)
    fig.update_yaxes(title_text='Overall Mean Price', row=2, col=1)
    
    return fig

# Client-side callback for navigation
app.clientside_callback(
    """
    function(units_clicks, price_clicks) {
        const triggered = dash_clientside.callback_context.triggered;
        if (triggered.length > 0) {
            const button_id = triggered[0]['prop_id'].split('.')[0];
            if (button_id === 'units-link') {
                return '/units';
            } else if (button_id === 'price-link') {
                return '/price';
            }
        }
        return '/units';
    }
    """,
    Output('url', 'pathname'),
    [Input('units-link', 'n_clicks'),
     Input('price-link', 'n_clicks')]
)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)