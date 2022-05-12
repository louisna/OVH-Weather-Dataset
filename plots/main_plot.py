"""
Main function for plotting

Usage:
$>python/ main_plot.py -m <metric to be considered> -e <plot extension>

Accepted values:
    metric: Timeline, Infrastructure, ...
    plot extension: PDF, PNG, EPS (optional argument)

__author__  = "Benoit Donnet (ULiege -- Institut Montefiore)"
__version__ = "1.0"
__date__    = "12/05/2022"
"""

import argparse
import sys, os

from Timeline import *
from Infrastructure import *
from Utils_Benoit import *

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--metric', action='store', type=str, required=True, help="metric to be considered (e.g., Timeline)")
    parser.add_argument('-e', '--extension', action='store', type=str, required=False, help="plot extension (PDF, PNG, EPS)")

    args = parser.parse_args()

    ext = retrieve_extension(args.extension)

    if args.metric=="Infrastructure":
        #plot_infra_evol(["../csv/nb-nodes-all.csv"], 'Nb Routers', ["EU"] , "../figures/nb-nodes-evolution."+ext, 183, 204)
        plot_infra_evol(["../csv/nb-links-all.csv"], 'NbLinks', ["EU"] , "../figures/nb-links-evolution."+ext, 860, 975)

    if args.metric=="Timeline":
        plot_timeline_dataset("../figures/timeline."+ext)
        plot_interval_dataset("../figures/files_distance."+ext)

if __name__ == "__main__":
    main(sys.argv[1:])
