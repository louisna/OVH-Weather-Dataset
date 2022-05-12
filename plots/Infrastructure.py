"""
Infrastructure plotting
#nodes
#links
node degree distribution
"""

from Utils_Benoit import *

def plot_infra_evol(csv_files, ylabel, labels, output, ymin, ymax):
    """
    Plots infrastructure (#nodes, #links) evolution over time

    Args:
        csv_files: input CSV files
        ylabel: ylabel string
        labels: datacenter to consider
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
    fig = figure()
    ax = fig.add_axes([0.13, 0.13, 0.85, 0.83])

    #style
    colors = ['#1f78b4', '#a6cee3','#33a02c', '#b2df8a']
    lstyles = ["dashdotted", "dashed", "solid"]

    #plot
    for i, (x, y) in enumerate(zip(all_x, all_data)):
        ax.plot(x, y, label=labels[i], color=colors[i], linewidth=2)

    axis_aesthetic(ax)
    ax.set_ylabel(latex_label(ylabel), font)
    ax.set_xlabel(latex_label('Time'), font)
    fig.autofmt_xdate(ha="center")

    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ylim(ymin, ymax)

    ax.grid(True, color='gray', linestyle='dashed')

    #save figure
    savefig(output, bbox_inches='tight')
