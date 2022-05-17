"""
Plots OVH ECMP. Bad copy of the other plot files (ECMP.py)

__author__  = "Louis Navarre (UCLouvain - IP Networking Lab"
__version__ = "1.0"
__date__    = "16/05/2022"
"""

from Utils_Benoit import *
from tqdm import tqdm
import matplotlib.dates as mdates
import pickle


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
        print(timestamp)
        hour_list.extend(data_vec)
        aggr[hour] = hour_list
    return aggr


def aggregate_per_day(x, data):
    aggr = dict()
    for timestamp, data_vec in zip(x, data):
        day = timestamp_into_day(timestamp)
        day_list = aggr.get(day, list())
        day_list.extend(data_vec)
        aggr[day] = day_list
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

    pickle_filename = "../csv/loads.data"
    try:
        with open(pickle_filename, "rb") as pickle_fd:
            all_data, all_x, max_values = pickle.load(pickle_fd)
            print("USED PICKLE")
    except Exception as e:
        print("Cannot use pickle", e)

        for file in csv_files:
            data_file = list()
            x = list()
            with open(file) as fd:
                for line in tqdm(fd.readlines()):
                    tab = line.split(": [")
                    timestamp = int(tab[0])
                    # timestamp = datetime.fromtimestamp(timestamp)
                    try:
                        data = [int(i) for i in tab[1][:-2].split(",")]
                        data_file.append(data)
                        x.append(timestamp)
                    except Exception as e:
                        print("Exception:", e)
                        continue
            all_x.append(x)
            all_data.append(data_file)
        all_data_aggregated = []
        for x, d in tqdm(zip(all_x, all_data)):
            all_data_aggregated.append(aggregate_week_day_hours(x, d))
        keys = all_data_aggregated[0].keys()
        sorted(keys)
        max_values = [max(all_data_aggregated[0][i]) for i in keys]
        all_data = cbook.boxplot_stats(all_data_aggregated[0].values(), labels=all_data_aggregated[0].keys(), whis=(1, 99))
        with open(pickle_filename, "wb+") as fd:
            pickle.dump((all_data, all_x, max_values), fd)
    
    fig = figure()
    ax = fig.add_axes([0.13, 0.13, 0.85, 0.83])

    colors = ['#1b9e77','#d95f02','#7570b3']  # https://colorbrewer2.org/#type=qualitative&scheme=Dark2&n=3
    lstyles = ["solid", "dotted", "densely dashed"]
    medianprops = dict(linewidth=3.5, color=colors[1])
    
    #all_data_aggregated = []
    #for x, d in tqdm(zip(all_x, all_data)):
    #     all_data_aggregated.append(aggregate_week_day_hours(x, d))
    #for data_file in all_data_aggregated:
    all_data = sorted(all_data, key=lambda i: i["label"])
    print(all_data)
    bplot = ax.bxp(all_data, showfliers=False, medianprops=medianprops, patch_artist=True)
    x_value = [i["label"] for i in all_data]
    x_value = sorted(x_value)
    hours = [
        i+1 for i in x_value if i % 2 == 0
    ]
    for patch in bplot["boxes"]:
        patch.set_facecolor(colors[0])
    #max_values = [max(i) for i in all_data.values()]
    print(max_values)
    plt.scatter([i + 1 for i in x_value], max_values, color=colors[2], marker="^", s=60)
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


def plot_one_boxplot_per_day(csv_files, ylabel, output, ymin, ymax):
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

    pickle_filename = "../csv/loads_per_day.data"
    try:
        with open(pickle_filename, "rb") as pickle_fd:
            all_data, all_x, max_values = pickle.load(pickle_fd)
            print("USED PICKLE")
    except Exception as e:
        print("Cannot use pickle", e)

        for file in csv_files:
            data_file = list()
            x = list()
            with open(file) as fd:
                for line in tqdm(fd.readlines()):
                    tab = line.split(": [")
                    timestamp = int(tab[0])
                    # timestamp = datetime.fromtimestamp(timestamp)
                    try:
                        data = [int(i) for i in tab[1][:-2].split(",")]
                        data_file.append(data)
                        x.append(timestamp)
                    except Exception as e:
                        print("Exception:", e)
                        continue
            all_x.append(x)
            all_data.append(data_file)
        all_data_aggregated = []
        for x, d in tqdm(zip(all_x, all_data)):
            all_data_aggregated.append(aggregate_per_day(x, d))
        keys = all_data_aggregated[0].keys()
        keys = sorted(keys)
        max_values = [max(all_data_aggregated[0][i]) for i in keys]
        all_data = cbook.boxplot_stats(all_data_aggregated[0].values(), labels=all_data_aggregated[0].keys(), whis=(1, 99))
        with open(pickle_filename, "wb+") as fd:
            pickle.dump((all_data, all_x, max_values), fd)
    
    fig = figure()
    ax = fig.add_axes([0.13, 0.13, 0.85, 0.83])

    colors = ['#1b9e77','#d95f02','#7570b3']  # https://colorbrewer2.org/#type=qualitative&scheme=Dark2&n=3
    lstyles = ["solid", "dotted", "dashed"]
    medianprops = dict(linewidth=3.5, color=colors[1])
    
    all_data = sorted(all_data, key=lambda i: i["label"])
    print(all_data)
    bplot = ax.bxp(all_data, showfliers=False, medianprops=medianprops, patch_artist=True)
    x_value = [i["label"] for i in all_data]
    x_value = sorted(x_value)
    hours = [
        i+1 for i in x_value if i % 2 == 0
    ]
    for patch in bplot["boxes"]:
        patch.set_facecolor(colors[0])
    print(max_values)
    plt.scatter([i + 1 for i in x_value], max_values, color=colors[2], marker="^", s=60)
    # ax.set_xticklabels(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    ax.set_xticklabels(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"])
    
    axis_aesthetic(ax)
    ax.set_ylabel(latex_label(ylabel), font)
    ax.set_xlabel(latex_label('Day of the week'), font)

    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ylim(ymin, ymax)

    ax.grid(True, color='gray', linestyle='dashed')

    # legend(fontsize=FONT_SIZE_LEGEND-5, bbox_to_anchor=(0.95, 1.1), ncol=3, handlelength=3)

    #save figure
    savefig(output, bbox_inches='tight')
    

def plot_all_loads_in_cdf(csv_files, labels, ylabel, output):
    """
    Plots traffic load over the (almost) two years of data we collected

    Args:
        csv_files: input CSV files
        labels: legend labels
        output: output file name
    """
    all_data = list()

    for file in csv_files:
        data_file = list()
        with open(file) as fd:
            for line in tqdm(fd.readlines()):
                try:
                    tab = line.split(": [")
                    # timestamp = datetime.fromtimestamp(timestamp)
                    data = [int(i) for i in tab[1][:-2].split(",")]
                    data_file.append(data)
                except Exception as e:
                    print("Exception:", e)
                    continue
        all_data.append(data_file)
    
    # Flatten all lists into a major list
    all_data_flatten = list()
    for data_file in all_data:
        data_flatten = list()
        for data in data_file:
            data_flatten += data
        all_data_flatten.append(data_flatten)
    
    # CDF computation
    all_bins = list()
    all_cdfs = list()
    max_data = 0
    for data_file in all_data_flatten:
        bins, cdf = compute_cdf(data_file, nb_bins=500)
        all_bins.append(bins)
        all_cdfs.append(cdf)
        max_data = max(max_data, max(data_file))

    # Create figure
    fig = figure()
    ax = fig.add_axes([0.13, 0.13, 0.85, 0.83])

    # Style
    colors = ['#1b9e77','#d95f02','#7570b3']  # https://colorbrewer2.org/#type=qualitative&scheme=Dark2&n=3
    if len(csv_files) == 1:
        colors[0] = colors[1]
    lstyles = ["solid", "dotted", "densely dashed"]

    for i, (bins, cdf) in enumerate(zip(all_bins, all_cdfs)):
        ax.step(bins, cdf, label=labels[i], color=colors[i], lw=2, ls=linestyles[lstyles[i]])

    axis_aesthetic(ax)
    ax.set_ylabel(latex_label('CDF'), font)
    ax.set_xlabel(latex_label('Load (\%)'), font)

    ax.set_xticks(list(range(0, 101, 10)))

    ax.grid(True, color='gray', linestyle='dashed')

    legend(fontsize=FONT_SIZE_LEGEND-5, bbox_to_anchor=(0.95, 1.1), ncol=3, handlelength=3)

    #save figure
    savefig(output, bbox_inches='tight')

    with open("../test_parsing/backup_load_cdf.txt", "w+") as fd:
        fd.write(f"{all_bins}\n{all_cdfs}")