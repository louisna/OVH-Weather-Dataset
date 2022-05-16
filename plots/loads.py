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
    Plots load in usage over time

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


def timestamp_into_day(timestamp: int) -> int:
    return datetime.fromtimestamp(timestamp).weekday()


def timestamp_into_hour_floor(timestamp: int) -> int:
    return datetime.fromtimestamp(timestamp).hour


def aggregate_week_day_hours(x, data):
    # For each file data, we will aggregate the data per hour. We will in a first step only take the the week days
    aggr = dict()  # Key: hour, value: data points list
    for timestamp, data_vec in zip(x, data):
        day = timestamp_into_day(timestamp)
        # if day < 4: continue  # Weekend
        hour = timestamp_into_hour_floor(timestamp)
        hour_list = aggr.get(hour, list())
        aggr[hour] = hour_list + data_vec
    return aggr


def plot_load_boxplot_week(csv_files, ylabel, output, ymin, ymax):
    """
    Plots load in usage over time with boxplots

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
                # timestamp = datetime.fromtimestamp(timestamp)
                data = [int(i) for i in tab[1][:-2].split(",")]
                data_file.append(data)
                x.append(timestamp)
        all_x.append(x)
        all_data.append(data_file)
    
    fig = figure()
    ax = fig.add_axes([0.13, 0.13, 0.85, 0.83])

    colors = ['#1b9e77','#d95f02','#7570b3']  # https://colorbrewer2.org/#type=qualitative&scheme=Dark2&n=3
    lstyles = ["solid", "dotted", "dashed"]
    medianprops = dict(linewidth=2.5, color=colors[1])
    
    all_data_aggregated = [aggregate_week_day_hours(x, d) for x, d in zip(all_x, all_data)]
    for data_file in all_data_aggregated:
        bplot = ax.boxplot(data_file.values(), whis=(1,99), showfliers=False, medianprops=medianprops, patch_artist=True)
        x_value = [list(data_file.keys())[i] + 1 for i in range(len(data_file.keys()))]
        hours = [
            i for i in x_value if i % 2 == 0
        ]
        for patch in bplot["boxes"]:
            patch.set_facecolor(colors[0])
        max_values = [max(i) for i in data_file.values()]
        plt.scatter(x_value, max_values, color=colors[2], marker="^")
        ax.set_xticks(hours)
        ax.set_xticklabels(list(range(24))[::2])
    
    axis_aesthetic(ax)
    ax.set_ylabel(latex_label(ylabel), font)
    ax.set_xlabel(latex_label('Time (hour)'), font)

    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ylim(ymin, ymax)

    ax.grid(True, color='gray', linestyle='dashed')

    # legend(fontsize=FONT_SIZE_LEGEND-5, bbox_to_anchor=(0.95, 1.1), ncol=3, handlelength=3)

    #save figure
    savefig(output, bbox_inches='tight')
    