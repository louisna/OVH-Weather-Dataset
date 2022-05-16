"""
Plots OVH ECMP. Bad copy of the other plot files (ECMP.py)

__author__  = "Louis Navarre (UCLouvain - IP Networking Lab"
__version__ = "1.0"
__date__    = "16/05/2022"
"""

from Utils_Benoit import *
from tqdm import tqdm
import matplotlib.dates as mdates


def plot_load_time_series(csv_files, ylabel, output, ymin, ymax):
    """
    Plots infrastructure load in usage over time

    Args:
        csv_files: input CSV files
        ylabel: ylabel string
        output: output filename
        ymin: min y-axis tick value
        ymax: max y-axis tick value
    """
    all_data = list()
    all_x = list()

    for file in csv_files:
        data_file = list()
        x = list()
        with open(file) as fd:
            for line in tqdm(fd.readlines()):
                tab = line.split(": [")
                timestamp = int(tab[0])
                timestamp = datetime.fromtimestamp(timestamp)
                data = [int(i) for i in tab[1][:-2].split(",")]
                data_file.append(data)
                x.append(timestamp)
        all_x.append(x)
        all_data.append(data_file)
    
    fig = figure()
    ax = fig.add_axes([0.13, 0.13, 0.85, 0.83])

    colors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c']  # https://colorbrewer2.org/#type=qualitative&scheme=Dark2&n=3
    lstyles = ["solid", "dotted", "dashed"]
    percentiles = [99, 95, 90, 50]
    percentiled_data = [list() for _ in range(len(percentiles))]

    for x, data in zip(all_x, all_data):
        for time_data in data:
            percs = np.percentile(time_data, percentiles)
            for i, perc in enumerate(percs):
                percentiled_data[i].append(perc)
    
    for i, percentile_data in enumerate(percentiled_data):
        ax.fill_between(all_x[0], percentile_data, color=colors[i], label=f"{percentiles[i]}th")

    axis_aesthetic(ax)
    ax.set_ylabel(latex_label(ylabel), font)
    ax.set_xlabel(latex_label('Time'), font)
    myFmt = mdates.DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(myFmt)
    fig.autofmt_xdate(ha="center")

    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ylim(ymin, ymax)

    ax.grid(True, color='gray', linestyle='dashed')

    legend(fontsize=FONT_SIZE_LEGEND-5, bbox_to_anchor=(0.95, 1.1), ncol=3, handlelength=3)

    #save figure
    savefig(output, bbox_inches='tight')