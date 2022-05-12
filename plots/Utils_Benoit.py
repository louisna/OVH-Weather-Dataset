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
import matplotlib.dates as mdates


rc('text', usetex=True)
rc('font',family='Times New Roman')
rc('xtick', labelsize='40')
rc('ytick', labelsize='40')
rc('lines', markersize=5)
rc('legend', numpoints=1)

#    date_labels=["16-05","16-06","16-07","16-08","16-09","16-10","16-11","16-12",
#                 "17-01","17-02","17-03","17-04","17-05","17-06","17-07","17-08",
#                 "17-09","17-10","17-11","17-12","18-01","18-02","18-03","18-04",
#                 "18-05","18-06","18-07","18-08","18-09","18-10","18-11","18-12",
#                 "19-01","19-02","19-03","19-04","19-05","19-06","19-07","19-08",
#                 "19-09","19-10","19-11","19-12","20-01","20-02","20-03","20-04",
#                 "20-05","20-06","20-07","20-08","20-09","20-10","20-11","20-12",
#                 "21-01","21-02","21-03","21-04","21-05","21-06","21-07","21-08",
#                 "21-09","21-10","21-11","21-12"]

"""
Dates for RIPE Atlas dataset
"""
date_labels=["16-05","","16-07","","16-09","","16-11","",
             "17-01","","17-03","","17-05","","17-07","","17-09","","17-11","",
             "18-01","","18-03","","18-05","","18-07","","18-09","","18-11","",
             "19-01","","19-03","","19-05","","19-07","","19-09","","19-11","",
             "20-01","","20-03","","20-05","","20-07","","20-09","","20-11","",
             "21-01","","21-03","","21-05","","21-07","","21-09","","21-11",""]

sr_label_range = ["[15,16[","[16,17[","[17,18[","[18,19[", "[19,20[","[20,21[",
                  "[21,22[","[22,23[","[23,24["]

#mpls_label_range = ['[0,25[', '[25,50[', '[50,75[', '[75,100[', '[100,125[',
#                    '[125,150[', '[150,175[', '[175,200[', '[200,225[', '[225,250[',
#                    '[250,275[', '[275,300[', '[300,325[','[325,350[', '[350,375[',
#                    '[375,400[', '[400,425[', '[425,450[','[450,475[', '[475,500[',
#                    '[500,575[', '[575,600[', '[600,625[','[625,650[', '[650,675[',
#                    '[675,700[', '[700,725[', '[725,750[','[750,775[', '[775,800[',
#                    '[800,825[', '[825,850[', '[850,875[','[875,900[', '[900,925[',
#                    '[925,1000[', '[1000,1025[', '[1025,1050[']

mpls_label_range = ['[0,25[', '', '[50,75[', '', '[100,125[', '', '[150,175[', '',
                    '[200,225[', '', '[250,275[', '', '[300,325[', '', '[350,375[', '',
                    '[400,425[', '', '[450,475[', '', '[500,575[', '', '[600,625[', '',
                    '[650,675[', '', '[700,725[', '', '[750,775[', '', '[800,825[', '',
                    '[850,875[', '', '[900,925[', '', '[1000,1025[', '']

"""
Font dictionary.

Used by (nearly) every plotting functions
"""

FONT_SIZE = 30
FONT_SIZE_TICKS = 30
FONT_SIZE_LEGEND = 15
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

def axis_aesthetic(ax, spine_position=10, axis_width=0.25, label_size=20, tick_length=4, tick_width=2):
    """
    General aesthetic of the plot.
    Args:
        ax: plot axis
        spine_position: space between the axis and the graph itself (10 by default)
        label_size: ticks label size (20 by default)
        tick_length: tick length (4 by default)
        tick_width: tick width (2 by default)
    """
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.spines['left'].set_position(('outward', spine_position))
    ax.spines['bottom'].set_position(('outward', spine_position))

    ax.spines['left'].set_linewidth(axis_width)
    ax.spines['bottom'].set_linewidth(axis_width)

    ax.tick_params(axis='both', which='major', labelsize=label_size)

    ax.tick_params(direction='inout', length=tick_length, width=tick_width)
