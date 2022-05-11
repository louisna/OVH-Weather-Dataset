import matplotlib.pyplot as plt
import numpy as np
import csv
from datetime import datetime
from utils import latexify, compute_cdf

def plot_nb_evolution(csv_file, ylabel, savefig = None):
    with open(csv_file) as fd:
        data = [i for i in csv.reader(fd)]
    
    fig, ax = plt.subplots()
    x, y = [int(i) for i in data[0]], [int(i) for i in data[1]]
    ax.plot(x, y)
    x_date = [datetime.fromtimestamp(i) for i in x]
    ax.set_xticklabels(x_date, rotation=45)
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    plt.show()


def plot_node_degree_cdf(csv_files, labels):
    all_data = list()
    for file in csv_files:
        with open(file) as fd:
            data = [int(i[0]) for i in csv.reader(fd)]
            all_data.append(data)
    print(all_data)
    all_bins = list()
    all_cdfs = list()
    for data in all_data:
        bins, cdf = compute_cdf(data, nb_bins=400)
        all_bins.append(bins)
        all_cdfs.append(cdf)
    
    fig, ax = plt.subplots()
    ax.set_ylabel("CDF")
    ax.set_xlabel("Node degree")
    colors = ['#1f78b4', '#a6cee3','#33a02c', '#b2df8a']
    linestyles = ["-.", "--", "-"]
    for i, (bins, cdf) in enumerate(zip(all_bins, all_cdfs)):
        ax.plot(bins, cdf, label=labels[i], color=colors[i], linestyle=linestyles[i])
    plt.legend(frameon=False, facecolor="white", edgecolor="white", framealpha=0)
    plt.tight_layout()
    plt.savefig("../figures/node-degree_09_05.pdf")
    plt.show()
    

if __name__ == "__main__":
    latexify(fig_width=3.39)
    # plot_nb_evolution("../ovh-parsing/output.csv", ylabel="Nb routers evolution")
    plot_node_degree_cdf(["../csv/static_node_degree_peers.csv", "../csv/static_node_degree_internal.csv", "../csv/static_node_degree.csv"], labels=["Peers", "OVH", "All"])