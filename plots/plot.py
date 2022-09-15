import matplotlib.pyplot as plt
import numpy as np
import csv
from datetime import datetime
from utils import latexify, compute_cdf
from matplotlib.ticker import MaxNLocator
from Utils_Benoit import *

def plot_nb_evolution(csv_files, ylabel, labels, savefig=None, show=True):
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

    fig, ax = plt.subplots()
    colors = ['#1f78b4', '#a6cee3','#33a02c', '#b2df8a']
    linestyles = ["-.", "--", "-"]
    for i, (x, y) in enumerate(zip(all_x, all_data)):
        ax.plot(x, y, label=labels[i], color=colors[i])
    ax.set_ylabel(ylabel)
    fig.autofmt_xdate(ha="center")
    plt.legend(frameon=False, facecolor="white", edgecolor="white", framealpha=0)
    plt.tight_layout()
    # Force to use integer numbers
    ax = fig.gca()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    if savefig is not None:
        plt.savefig(savefig)
    if show:
        plt.show()


def plot_node_degree_cdf(csv_files, labels):
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

    fig, ax = plt.subplots()
    ax.set_ylabel("Complementary CDF")
    ax.set_xlabel("Node degree")
    colors = ['#1f78b4', '#a6cee3','#33a02c', '#b2df8a']
    linestyles = ["-.", "--", "-"]
    for i, (bins, cdf) in enumerate(zip(all_bins, all_cdfs)):
        ax.plot(bins, cdf, label=labels[i], color=colors[i], linestyle=linestyles[i])
    plt.legend(frameon=False, facecolor="white", edgecolor="white", framealpha=0)
    plt.tight_layout()
    ax.set_xticks(list(range(1, max_data + 1, 2)))
    # ax.set_yticks([0.0, 0.25, 0.50, 0.75, 1.0])
    plt.savefig("../figures/node-degree_09_05.pdf")
    plt.show()


if __name__ == "__main__":
    latexify()
    #plot_nb_evolution(["../ovh-parsing/csv/nb-nodes.csv"], labels=["EU"], ylabel="Nb routers evolution", show=False, savefig="../figures/nb-nodes-evolution.pdf")
    #plot_nb_evolution(["../ovh-parsing/csv/nb-links.csv"], labels=["EU"], ylabel="Nb Links evolution", show=False, savefig="../figures/nb-links-evolution.pdf")
    plot_node_degree_cdf(["../csvCR/static_node_degree_peers.csv", "../csvCR/static_node_degree_internal.csv", "../csvCR/static_node_degree.csv"], labels=["Peers", "OVH", "All"])
