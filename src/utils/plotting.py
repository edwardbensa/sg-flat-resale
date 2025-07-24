from pathlib import Path
import sys

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image
import io
import os

from src import config


# Create a custom colourmap
colours = ["#ff4500", "#faa272", "#ffdab9", "#0088ff", "#003376"]
cmap = mcolors.LinearSegmentedColormap.from_list("", colours)

# Function creation
def multi_stop_gradient(n):
    colours_rgb = [np.array(mcolors.to_rgb(colour)) for colour in colours]
    result = []
    
    for i in range(n):
        # Map i to the continuous range [0, len(colours)-1]
        pos = i * (len(colours) - 1) / (n - 1)
        
        # Find the segment
        segment = int(pos)
        if segment >= len(colours) - 1:
            segment = len(colours) - 2
        
        # Interpolate within the segment
        ratio = pos - segment
        interpolated = colours_rgb[segment] + (colours_rgb[segment + 1] - colours_rgb[segment]) * ratio
        result.append(mcolors.to_hex(interpolated))
    
    return result

def catplots(df, x_vars, group_by, title, agg_operation = 'count'):
    fig = make_subplots(rows=2, cols=1, row_heights=[2, 0.5])
    group_values = sorted(df[group_by].unique())
    n_groups = len(group_values)
    colors = multi_stop_gradient(n_groups)
    color_map = dict(zip(group_values, colors))
    
    # Create traces for line and bar plots
    for x_var in x_vars:
        if agg_operation == 'median':
            df_plot = df.groupby([x_var, group_by])['infl_adj_price'].median().reset_index()
            df_plot_all = df.groupby(x_var)['infl_adj_price'].median().reset_index()
        elif agg_operation == 'mean':
            df_plot = df.groupby([x_var, group_by])['infl_adj_price'].mean().reset_index()
            df_plot_all = df.groupby(x_var)['infl_adj_price'].mean().reset_index()
        else:
            df_plot = df.groupby([x_var, group_by]).size().reset_index(name='units_resold')
            df_plot_all = df.groupby(x_var).size().reset_index(name='units_resold')
        
        if agg_operation == 'count':
            y_var = 'units_resold'
        else:
            y_var = 'infl_adj_price'

        # Add line traces for each group
        for g in group_values:
            df_g = df_plot[df_plot[group_by] == g]
            fig.add_trace(go.Scatter(
                x=df_g[x_var],
                y=df_g[y_var],
                mode='lines',
                name=g,
                line=dict(color=color_map[g]),
                visible=(x_var == x_vars[0]),  # Only show first x_var initially
                legendgroup=g,
                showlegend=True
            ), row=1, col=1)
        
        # Add line trace for all
        fig.add_trace(go.Scatter(
            x=df_plot_all[x_var],
            y=df_plot_all[y_var],
            mode='lines',
            name='All',
            line=dict(color='gray'),
            visible=(x_var == x_vars[0]),
            legendgroup='All',
            showlegend=True
        ), row=2, col=1)
        
        # Add bar traces for each group
        for g in group_values:
            df_g = df_plot[df_plot[group_by] == g]
            fig.add_trace(go.Bar(
                x=df_g[x_var],
                y=df_g[y_var],
                name=g,
                marker=dict(color=color_map[g]),
                visible=False,  # Hidden initially
                legendgroup=g,
                showlegend=True
            ), row=1, col=1)
        
        # Add bar trace for all
        fig.add_trace(go.Bar(
            x=df_plot_all[x_var],
            y=df_plot_all[y_var],
            name='All',
            marker=dict(color='gray'),
            visible=False,  # Hidden initially
            legendgroup='All',
            showlegend=True
        ), row=2, col=1)
    
    # Calculate trace indices
    traces_per_x_var = 2 * (n_groups + 1)  # line + bar traces for each x_var
    
    # Create dropdown buttons for x-axis variable
    x_axis_dropdown_buttons = []
    for i, x_var in enumerate(x_vars):
        visibility = [False] * len(fig.data)
        
        # Show line traces for this x_var (default)
        start_idx = i * traces_per_x_var
        line_end_idx = start_idx + n_groups + 1
        for j in range(start_idx, line_end_idx):
            if j < len(visibility):
                visibility[j] = True
        
        x_axis_dropdown_buttons.append(dict(
            args=[
                {"visible": visibility},
                {
                    "xaxis.title": x_var.replace('_', ' ').title(),
                    "xaxis2.title": x_var.replace('_', ' ').title()
                }
            ],
            label=x_var.replace('_', ' ').title(),
            method="update"
        ))
    
    # Create buttons for plot type
    plot_type_buttons = []
    
    # Line plot button
    def get_line_visibility():
        visibility = [False] * len(fig.data)
        # Show line traces for first x_var
        for j in range(n_groups + 1):
            if j < len(visibility):
                visibility[j] = True
        return visibility
    
    # Bar plot button  
    def get_bar_visibility():
        visibility = [False] * len(fig.data)
        # Show bar traces for first x_var
        start_idx = n_groups + 1
        for j in range(start_idx, start_idx + n_groups + 1):
            if j < len(visibility):
                visibility[j] = True
        return visibility
    
    plot_type_buttons.append(dict(
        args=[
            {"visible": get_line_visibility()},
            {"barmode": "group"}
        ],
        label="Line Plot",
        method="update"
    ))
    
    plot_type_buttons.append(dict(
        args=[
            {"visible": get_bar_visibility()},
            {"barmode": "stack"}
        ],
        label="Bar Plot", 
        method="update"
    ))
    
    if agg_operation == 'median':
        y_title = 'Median Resale Price (S$)'
    elif agg_operation == 'mean':
        y_title = 'Mean Resale Price (S$)'
    else:
        y_title = 'Units Resold'

    fig.update_layout(
        autosize=False,
        title=dict(text=title, y=0.95),
        yaxis_title=y_title,
        xaxis_title=x_vars[0].replace('_', ' ').title(),
        xaxis2_title=x_vars[0].replace('_', ' ').title(),
        width=1100,
        height=500,
        margin=dict(l=20, r=20, t=100, b=20),
        bargap=0.15,
        updatemenus=[
            # X-axis variable dropdown
            dict(
                buttons=x_axis_dropdown_buttons,
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=1.01,
                xanchor="right",
                y=1.15,
                yanchor="top"
            ),
            # Plot type radio buttons
            dict(
                buttons=plot_type_buttons,
                direction="right",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.26,
                xanchor="right",
                y=1.15,
                yanchor="top",
                type="buttons"
            )
        ],
        annotations=[
            dict(
                text="Select X-axis Variable:",
                showarrow=False,
                x=0.86,
                y=1.1,
                xref="paper",
                yref="paper"
            ),
            dict(
                text="Plot Type:",
                showarrow=False,
                x=0,
                y=1.1,
                xref="paper",
                yref="paper"
            )
        ]
    )
    
    fig.show()