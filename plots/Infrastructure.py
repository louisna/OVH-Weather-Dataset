"""
OVH infrastructure plotting (#nodes, #links, node degree distribution)

__author__  = "Benoit Donnet (ULiege -- Institut Montefiore)"
__version__ = "1.0"
__date__    = "12/05/2022"
"""

from datetime import timedelta
from Utils_Benoit import *

def plot_node_degree(csv_files, labels, output):
    """
    Plots node degree distribution

    Args:
        csv_files: input CSV files
        labels: legend labels
        output: output file name
    """
    #get data
    all_data = list()
    for file in csv_files:
        with open(file) as fd:
            data = [int(i[0]) for i in csv.reader(fd)]
            all_data.append(data)
    all_bins = list()
    all_cdfs = list()
    max_data = 0
    for data in all_data:
        bins, cdf = compute_cdf(data, nb_bins=400)
        all_bins.append(bins)
        all_cdfs.append([1 - i for i in cdf])
        max_data = max(max_data, max(data))

    #create figure
    fig = figure(figsize=(8,4))
    ax = fig.add_axes([0.13, 0.13, 0.85, 0.83])

    #style
    colors = ['#1b9e77','#d95f02','#7570b3']  # https://colorbrewer2.org/#type=qualitative&scheme=Dark2&n=3
    if len(csv_files) == 1:
        colors[0] = colors[1]
    lstyles = ["solid", "dotted", "dashed"]

    for i, (bins, cdf) in enumerate(zip(all_bins, all_cdfs)):
        ax.step(bins, cdf, label=labels[i], color=colors[i], lw=2, ls=linestyles[lstyles[i]])

    axis_aesthetic(ax)
    ax.set_ylabel(latex_label('CCDF'), font)
    ax.set_xlabel(latex_label('Node Degree'), font)

    # ax.set_xticks([1, 20, 40, 60, 80, 100])
    ax.set_ylim(0, 0.8)

    ax.grid(True, color='gray', linestyle='dashed')

    #legend(fontsize=FONT_SIZE_LEGEND-4, bbox_to_anchor=(0.95, 1.1), ncol=3, handlelength=3)
    ax.legend().set_visible(False)

    #save figure
    savefig(output, bbox_inches='tight')

def plot_infra_evol(csv_files, ylabel, labels, output, ymin, ymax):
    """
    Plots infrastructure (#nodes, #links) evolution over time

    Args:
        csv_files: input CSV files
        ylabel: ylabel string
        labels: legend labels
        output: output filename
        ymin: min y-axis tick value
        ymax: max y-axis tick value
    """
    #get data
    all_data = list()
    all_x = list()
    for file in csv_files:
        with open(file) as fd:
            data = [i for i in csv.reader(fd)]
            # Parse into x/y
            x = [datetime.fromtimestamp(int(i[0])) for i in data]
            y = [int(i[1]) for i in data]
            all_x.append(x)
            all_data.append(y)

    #create figure
    fig = figure(figsize=(8,4))
    ax = fig.add_axes([0.13, 0.13, 0.85, 0.83])

    #style
    colors = ['#1b9e77','#d95f02','#7570b3']  # https://colorbrewer2.org/#type=qualitative&scheme=Dark2&n=3
    if len(csv_files) == 1:
        colors[0] = colors[1]
    lstyles = ["solid", "dotted", "dashed"]

    #plot
    for i, (x, y) in enumerate(zip(all_x, all_data)):
        subx = []
        suby = []
        for (dt1, dt2), (y1, y2) in zip(zip(x[:-1], x[1:]), zip(y[:-1], y[1:])):
            subx.append(dt1)
            suby.append(y1)
            if dt2 - dt1 > timedelta(hours=1):
                ax.plot(subx, suby, color=colors[i], lw=2, ls=linestyles[lstyles[0]]) # linestyle is kept the same otherwise gaps in the data can be mixed with linestyles
                subx = []
                suby = []
        if subx and suby:
            ax.plot(subx, suby, label=legend_label(labels[i]), color=colors[i], lw=2, ls=linestyles[lstyles[0]])

    axis_aesthetic(ax)
    ax.set_ylabel(latex_label(ylabel), font)
    ax.set_xlabel(latex_label('Time'), font)
    fig.autofmt_xdate(ha="center")

    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ylim(ymin, ymax)

    ax.grid(True, color='gray', linestyle='dashed')

    if len(labels)==1:
        ax.legend().set_visible(False)
    else:
        legend(fontsize=FONT_SIZE_LEGEND-4, bbox_to_anchor=(0.85, 1.15), ncol=3, handlelength=3)

    #save figure
    savefig(output, bbox_inches='tight')
