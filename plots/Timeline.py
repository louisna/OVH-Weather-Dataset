"""
WeatherMap timeline plotting
"""

import sys, os

#from yaml import load, dump
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from Utils_Benoit import *

INTERVAL_DIST = 6 * 60
all_intervals = {}
all_distances = {}
maps = {
    'data': 'Europe',
    'data_world': 'World',
    'data_usa': 'North America',
    'data_apac': 'Asia Pacific'
}

colors = ['#1f78b4', '#a6cee3','#33a02c', '#b2df8a']

def plot_interval_dataset(output):
    """
    Plots the time interval between 2 dataset snapshots

    Args:
        output: output filename
    """
    #create figure
    fig = figure(figsize=(8,4))
    ax = fig.add_axes([0.13, 0.13, 0.85, 0.83])

    #load data
    with open('../data_time_distances.yaml', 'r') as f:
        all_distances = yaml.load(f, Loader=Loader)

    for (data_dir, distances), c in zip(all_distances.items(), colors):
        plt.plot(list(sorted(distances)), [x / len(distances) for x in range(len(distances))], label=maps[data_dir], color=c, linewidth=2)

    #axis labels
    plt.ylabel(latex_label('CDF'), font)
    plt.xlabel(latex_label('Distance (sec.)'), font)

    #formatter
    formatter = ScalarFormatter()
    formatter.set_scientific(False)

    #xticks
    plt.xscale('log')
    xticks = [1, 300] + [300 * (2 ** i) for i in range(1, 16)]
    ax.set_xticks(xticks)
    ax.minorticks_off()
    ax.xaxis.set_major_formatter(formatter)

    #yticks
    plt.yscale('logit')
    ax.yaxis.set_major_formatter(formatter)

    #axis limits
    plt.xlim(250, 60*60*4)
    plt.ylim(0, 1)

    #axis stuffs
    axis_aesthetic(ax)

    legend(fontsize=FONT_SIZE_LEGEND, loc='lower right')
    ax.grid(True, color='gray', linestyle='dashed')

    #save figure
    savefig(output, bbox_inches='tight')

def plot_timeline_dataset(output):
    """
    Plots the timeline of collected data over time

    Args:
        output: output filename
    """
    #create figure
    fig = figure(figsize=(12,3))
    ax = fig.add_axes([0.13, 0.13, 0.85, 0.83])

    #load data
    with open('../data_time_intervals.yaml', 'r') as f:
        all_intervals = yaml.load(f, Loader=Loader)

    for (data_dir, intervals), c in reversed(list(zip(all_intervals.items(), colors))):
        plt.hlines(y=[''.join(filter(str.isupper, maps[data_dir])) for _ in intervals], xmin=[datetime.datetime.fromtimestamp(a) for a, _ in intervals], xmax=[datetime.datetime.fromtimestamp(b) for _, b in intervals], color=c, label=maps[data_dir], linewidth=6)

    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    ax.grid(axis='x', which='major', linewidth=2)
    fig.autofmt_xdate(ha='center')
    plt.xlim(datetime.datetime(2020, 6, 21), datetime.datetime.today())
    handles, labels = ax.get_legend_handles_labels()

    #axis stuffs
    axis_aesthetic(ax)
    xticks_labs = ['2020-07','2020-10','2021-01','2021-04','2021-07','2021-10',
                   '2022-01','2022-04']
    ax.tick_params(axis='both', which='major', labelsize=FONT_SIZE_TICKS)
    ax.set_xticklabels(xticks_labs, rotation=45)

    plt.legend(handles[::-1], labels[::-1], bbox_to_anchor=(0.95, 1.3), ncol=4, fontsize=FONT_SIZE_LEGEND)

    #save figure
    savefig(output, bbox_inches='tight')
