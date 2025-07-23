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