"""
Utils functions and wrappers for processing  statistics

__author__  = "Benoit Donnet (ULiege -- Institut Montefiore)"
__version__ = "1.0"
__date__    = "25/10/2020"
"""

#Import everything
from pylab import *
from matplotlib.font_manager import *
import seaborn as sns
import pandas as pd
import matplotlib.ticker as ticker
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from NormalizeColorBar import *
from matplotlib import gridspec
import matplotlib.colors as colors
from scipy.stats import *
from matplotlib.lines import Line2D
import plot_likert.plot_likert, plot_likert.colors
import matplotlib.pyplot as plt
from datetime import datetime
#import datetime
import matplotlib.dates as mdates
import csv
from utils import *


rc('text', usetex=True)
rc('font',family='Times New Roman')
rc('xtick', labelsize='40')
rc('ytick', labelsize='40')
rc('lines', markersize=5)
rc('legend', numpoints=1)

"""
Font dictionary.

Used by (nearly) every plotting functions
"""

FONT_SIZE = 40
FONT_SIZE_TICKS = 30
FONT_SIZE_LEGEND = 20
font = {
    'fontname'   : 'DejaVu Sans',
    'color'      : 'k',
    'fontsize'   : FONT_SIZE
       }
"""
Defines various linestyles for plotting

How to:
plot(..., ls=linestyles['dotted'])

Taken from https://matplotlib.org/3.1.0/gallery/lines_bars_and_markers/linestyles.html
"""
linestyle_tuple = [
     ('solid',                 (0, ())),
     ('loosely dotted',        (0, (1, 10))),
     ('dotted',                (0, (1, 1))),
     ('densely dotted',        (0, (1, 1))),

     ('loosely dashed',        (0, (5, 10))),
     ('dashed',                (0, (5, 5))),
     ('densely dashed',        (0, (5, 1))),

     ('loosely dashdotted',    (0, (3, 10, 1, 10))),
     ('dashdotted',            (0, (3, 5, 1, 5))),
     ('densely dashdotted',    (0, (3, 1, 1, 1))),

     ('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
     ('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))),
     ('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1)))]

linestyles = dict(linestyle_tuple)


def latex_label(s):
    """
    Format String for LaTeX style (axis label)
    __author__  = "Emeline Marechal (ULiege -- Institut Montefiore)"
    """
    title = r'\textrm{\textbf{' + s  + '}}'
    return title

def legend_label(s):
    """
    Format String for LaTeX style (ticks/legend label)
    __author__  = "Emeline Marechal (ULiege -- Institut Montefiore)"
    """
    #label = r'\textrm{\textbf{' + s + '}}'
    label = s
    return label

def to_cdf(array):
    """
    Builds a CDF distribution
    Args:
        array: data on which CDF must be built (float expected)

    Returns:
        CDF data
    """
    array.sort()
    array.append(array[-1])
    cum_dist = np.linspace(0.,1.,len(array))
    data_cdf = pd.Series(cum_dist, index=array)

    return data_cdf

def axis_aesthetic(ax, spine_position=10, axis_width=0.25, label_size=20, tick_length=4, tick_width=2, labels=True):
    """
    General aesthetic of the plot.
    Args:
        ax: plot axis
        spine_position: space between the axis and the graph itself (10 by default)
        label_size: ticks label size (20 by default)
        tick_length: tick length (4 by default)
        tick_width: tick width (2 by default)
        labels: whether to play with labels or not (True by default)
    """
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.spines['left'].set_position(('outward', spine_position))
    ax.spines['bottom'].set_position(('outward', spine_position))

    ax.spines['left'].set_linewidth(axis_width)
    ax.spines['bottom'].set_linewidth(axis_width)

    if labels:
        ax.tick_params(axis='both', which='major', labelsize=label_size)
    else:
        ax.tick_params(axis='both', labelsize=label_size)

    ax.tick_params(direction='inout', length=tick_length, width=tick_width)

def retrieve_extension(arg):
    if arg=="PDF":
        return "pdf"

    if arg=="EPS":
        return "eps"

    if arg=="PNG":
        return "png"

    return "pdf"
