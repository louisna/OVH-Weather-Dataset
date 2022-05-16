"""
Main function for plotting

Usage:
$>python/ main_plot.py -m <metric to be considered> -e <plot extension>

Accepted values:
    metric: Timeline, Infrastructure, ECMP, ...
    plot extension: PDF, PNG, EPS (optional argument)

__author__  = "Benoit Donnet (ULiege -- Institut Montefiore)"
__version__ = "1.0"
__date__    = "12/05/2022"
"""

import argparse
import sys, os

from Timeline import *
from Infrastructure import *
from ECMP import *
from loads import *
from Utils_Benoit import *

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--metric', action='store', type=str, required=True, help="metric to be considered (e.g., Timeline)")
    parser.add_argument('-e', '--extension', action='store', type=str, required=False, help="plot extension (PDF, PNG, EPS)")

    args = parser.parse_args()

    ext = retrieve_extension(args.extension)

    if args.metric=="ECMP":
        plot_ecmp_imbalance("../csv/ecmp-agg-values-all.csv", "../csv/ecmp-agg-total-all.csv",
                            "../figures/ecmp-imbalance."+ext)
        plot_ecmp_imbalance_time_series(["../csv_march_2022/ecmp-diffs-all.yaml"], "ECMP difference", "../figures/ecmp-ts-march-2022."+ext, 0, 20)

    if args.metric == "LOADS":
        # plot_load_time_series(["../csv_march_2022/loads-all.yaml"], "Links load", "../figures/load-ts-march-2022."+ext, 0, 100)
        plot_load_boxplot_week(["../csv_march_2022/loads-all.yaml"], "Links load (\%)", "../figures/load-ts-march-2022."+ext, 0, 100)

    if args.metric=="Infrastructure":
        plot_infra_evol(["../csv/nb-nodes-all.csv", "../csv/nb-nodes-ovh.csv", "../csv/nb-nodes-external.csv"],
        '\# Routers', ['All', 'OVH', 'External'] , "../figures/nb-nodes-evolution."+ext, 60, 210)
        plot_infra_evol(["../csv/nb-links-all.csv", "../csv/nb-links-ovh.csv", "../csv/nb-links-external.csv"],
        '\# Links', ['All', 'OVH', 'External'] , "../figures/nb-links-evolution."+ext, 100, 1000)
        plot_node_degree(["../csv/static_node_degree.csv", "../csv/static_node_degree_internal.csv", "../csv/static_node_degree_peers.csv"],
        ['All', 'OVH', 'Peers'], "../figures/node-degree_09_05."+ext)

    if args.metric=="Timeline":
        #plot_timeline_dataset("../figures/timeline."+ext)
        plot_interval_dataset("../figures/files_distance."+ext)

if __name__ == "__main__":
    main(sys.argv[1:])
