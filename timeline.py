from fileinput import filename
from nis import maps
import sys, os
from time import time
import datetime

import yaml


from matplotlib import pyplot as plt
from matplotlib.ticker import ScalarFormatter
import matplotlib.dates as mdates

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

if __name__ == "__main__":
    if all(os.path.exists(data_dir) for data_dir in maps):
        for data_dir in maps:
            filenames = list(sorted(os.listdir(data_dir)))
            intervals = []
            distances = []
            for f in filenames:
                timestamp = int(os.path.splitext(f)[0].split('_')[1])
                if len(intervals) == 0:
                    intervals.append([timestamp, timestamp])
                last_interval = intervals[-1]
                if last_interval:
                    distances.append(timestamp - last_interval[1])
                if timestamp - last_interval[1] <= INTERVAL_DIST:
                    last_interval[1] = timestamp
                    intervals[-1] = last_interval
                else:
                    intervals.append([timestamp, timestamp])
            all_intervals[data_dir] = intervals
            all_distances[data_dir] = distances

        with open('data_time_intervals.yaml', 'w') as f:
            yaml.dump(all_intervals, f)

        with open('data_time_distances.yaml', 'w') as f:
            yaml.dump(all_distances, f)
    else:
        with open('data_time_intervals.yaml', 'r') as f:
            all_intervals = yaml.load(f)

        with open('data_time_distances.yaml', 'r') as f:
            all_distances = yaml.load(f)

    fig, ax = plt.subplots(figsize=(8,2.5))
    for (data_dir, intervals), c in reversed(list(zip(all_intervals.items(), colors))):
        plt.hlines(y=[''.join(filter(str.isupper, maps[data_dir])) for _ in intervals], xmin=[datetime.datetime.fromtimestamp(a) for a, _ in intervals], xmax=[datetime.datetime.fromtimestamp(b) for _, b in intervals], color=c, label=maps[data_dir], linewidth=5)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    ax.grid(axis='x', which='major')
    fig.autofmt_xdate(ha='center')
    plt.xlim(datetime.datetime(2020, 6, 21), datetime.datetime.today())
    handles, labels = ax.get_legend_handles_labels()
    plt.legend(handles[::-1], labels[::-1], loc='center')
    plt.tight_layout()
    plt.savefig(f'timeline.pdf')

    fig, ax = plt.subplots(figsize=(8,4))
    for (data_dir, distances), c in zip(all_distances.items(), colors):
        plt.plot(list(sorted(distances)), [x / len(distances) for x in range(len(distances))], label=maps[data_dir], color=c)
    plt.ylabel('Percentage')
    plt.xlabel('Distance between consecutive files (seconds)')
    plt.xscale('log')
    xticks = [1, 300] + [300 * (2 ** i) for i in range(1, 16)]
    ax.set_xticks(xticks)
    ax.minorticks_off()
    formatter = ScalarFormatter()
    formatter.set_scientific(False)
    ax.xaxis.set_major_formatter(formatter)
    plt.yscale('logit')
    ax.yaxis.set_major_formatter(formatter)
    #ax.xaxi
    plt.xlim(250, 60*60*4)
    plt.ylim(0, 1)
    plt.legend()
    plt.tight_layout()
    plt.savefig('files_distance.pdf')
