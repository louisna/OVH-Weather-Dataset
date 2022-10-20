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
from peeringdb import *
from Utils_Benoit import *

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--metric', action='store', type=str, required=True, help="metric to be considered (e.g., Timeline)")
    parser.add_argument('-e', '--extension', action='store', type=str, required=False, help="plot extension (PDF, PNG, EPS)")

    args = parser.parse_args()

    ext = retrieve_extension(args.extension)

    if args.metric=="ECMP":
        plot_all_ecmp_imbalance_in_cdf(["../csvCR/ecmp-diffs-all.yaml", "../csvCR/ecmp-diffs-ovh.yaml", "../csvCR/ecmp-diffs-external.yaml"], ["All", "Internal", "External"], "ECMP imbalance (\%)", "../figures/ecmp-diff-cdf."+ext, (0, 10))

    if args.metric == "LOADS":
        plot_load_boxplot_week(["../csvCR/loads-all.yaml"], "Links load (\%)", "../figures/load-ts."+ext, 0, 100)
        plot_all_loads_in_cdf(["../csvCR/loads-all.yaml", "../csvCR/loads-ovh.yaml", "../csvCR/loads-external.yaml"], ["All", "Internal", "External"], "CDF", "../figures/load-cdf."+ext)

    if args.metric=="Infrastructure":
        # plot_infra_evol(["../csvCR/nb-nodes-ovh.csv"],
        # '\# Routers', [r"\textsc{OVH}"] , "../figures/nb-nodes-evolution."+ext, 108, 124)
        # plot_infra_evol(["../csvCR/nb-links-all.csv", "../csvCR/nb-links-ovh.csv", "../csvCR/nb-links-external.csv"],
        # '\# Links', ['All', 'Internal', 'External'] , "../figures/nb-links-evolution."+ext, 100, 1100)
        # plot_node_degree(["../csv/static_node_degree_internal.csv"],
        # [r"\textsc{OVH}"], "../figures/node-degree_09_05."+ext)
        plot_nb_link_and_node()

    if args.metric=="Timeline":
        plot_interval_dataset("../figures/files_distance."+ext)
        plot_timeline_dataset("../figures/timeline."+ext)

    if args.metric == "Peering":
        plot_peering_db_example(["../csvCR/AMS-IX_ams-5-n7.csv"], "../figures/peering-db-example."+ext)

if __name__ == "__main__":
    main(sys.argv[1:])

