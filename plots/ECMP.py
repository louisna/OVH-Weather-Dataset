"""
Plots OVH ECMP

__author__  = "Benoit Donnet (ULiege -- Institut Montefiore), Louis Navarre (UCLouvain - IP Networking Lab"
__version__ = "1.0"
__date__    = "14/05/2022"
"""

from Utils_Benoit import *
from matplotlib.colors import LogNorm, Normalize
from tqdm import tqdm
import matplotlib.dates as mdates

empty_date_label=["","","","","","","","","","","","","","","","","","","","","","","","",""]
yticklabels_heatmap = ['[0,1[','[1,2[','[2,3[','[3,4[','[4,5[','[5,6[','[6,7[','[7,100[']

def plot_ecmp_imbalance(values, total, output,figsize_x=24, figsize_y=15, cbar_center=0.05, max_ylim_total=3000000):
    """
    Plots ECMP imbalance in OVH through heatmap

    Args:
        values: imbalance values on a per month basis
        total: total of imbalance values on a per month basis
        output: output filename
        figsize_x: figure width (24 by default)
        figsize_y: figure height (15 by default)
        cbar_center: color bar center point (0.05 by default)
        max_ylim_total: max Y axis value for the below bar plot (3000000 by default)
    """
    #load data
    dfValues = pd.read_csv(values, sep=';', skipinitialspace=True, parse_dates=['Time'])
    dfTotal  = pd.read_csv(total, sep=';', skipinitialspace=True)

    #computes relative values
    dfValues = dfValues[yticklabels_heatmap]
    dfValues.loc[:,'[0,1[':'[7,100['] = dfValues.loc[:,'[0,1[':'[7,100['].div(dfValues.sum(axis=1), axis=0)

    #create subfigures
    f, ax = plt.subplots(1,1,figsize=(figsize_x,figsize_y))

    #global style
    sns.set(style="ticks",context="paper", color_codes=True, font_scale=2, font=font)

    #got time in format YYYY-MM
    dates = [datetime.fromtimestamp(ts).strftime('%Y-%m') for ts in dfTotal['Time']]
    dfTotal['Time'] = dates
    dfTotal.index = pd.to_datetime(dfTotal.index)

    ###########################
    # HeatMap                 #
    ###########################
    df = dfValues.transpose()

    midnorm = MidpointNormalize(vmin=0, vcenter=cbar_center, vmax=np.nanmax(df))
    df.replace(0, np.nan, inplace=True)
    mask = df.isnull()

    g = sns.heatmap(df, cbar_kws={'label': latex_label('Proportion'), "use_gridspec" : False,
                    "location":"top", "extend":"both", 'anchor':(0.2,0.2)},
                     xticklabels=dfTotal['Time'], yticklabels=yticklabels_heatmap,
                     norm=midnorm, cmap='coolwarm', annot=False, ax=ax, mask=mask)#, vmin=1, vmax=np.nanmax(df))

    ax.invert_yaxis()

    g.set_ylabel(latex_label('Imbalance (\%age)'), fontsize=FONT_SIZE)
    sns.despine(offset=10, top=True, right=True, left=False, bottom=False)

    # Color bar and size of ticks
    g.figure.axes[-1].xaxis.label.set_size(FONT_SIZE)
    g.collections[0].colorbar.ax.tick_params(labelsize=FONT_SIZE_TICKS)

    ax.tick_params(axis='both', which='major', labelsize=FONT_SIZE_TICKS)
    ax.tick_params(direction='inout', length=4, width=2)

    ax.set_xlabel(latex_label('Time'), font)
    ax.tick_params(axis='x', labelrotation=45)

    ###########################
    # BarPlot                 #
    ###########################
    #got time in format YYYY-MM
    #dates = [datetime.fromtimestamp(ts).strftime('%Y-%m') for ts in dfTotal['Time']]
    #dfTotal['Time'] = dates
    #dfTotal.index = pd.to_datetime(dfTotal.index)

    #dfTotal.plot(x='Time', y='Total', kind='bar', legend=False, ax=ax[1])

    #ax[1].semilogy()
    #ax[1].set_ylim(1, max_ylim_total)

    #axis_aesthetic(ax[1])

    #ax[1].set_xlabel(latex_label('Time'), font)
    #ax[1].set_ylabel(latex_label("Raw Number"), font)
    #ax[1].tick_params(axis='both', which='major', labelsize=FONT_SIZE_TICKS)
    #ax[1].tick_params(axis='x', labelrotation=45)

    #ax[1].grid(True, color='gray', linestyle='dashed')

    savefig(output, bbox_inches='tight')


def plot_ecmp_imbalance_time_series(csv_files, ylabel, output, ymin, ymax):
    """
    Plots infrastructure ECMP difference in usage over time

    Args:
        csv_files: input CSV files
        ylabel: ylabel string
        output: output filename
        ymin: min y-axis tick value
        ymax: max y-axis tick value
    """
    #get data
    all_data = list()
    all_x = list()
    for file in csv_files:
        data_file = list()
        with open(file) as fd:
            x = list()
            for k, line in tqdm(enumerate(fd.readlines())):
                tab = line.split(": [")
                timestamp = int(tab[0])
                timestamp = datetime.fromtimestamp(timestamp)
                # print(tab[1][:-2].split(","), k)
                data = [int(i) for i in tab[1][:-2].split(",")]
                data_file.append(data)
                x.append(timestamp)
        # Parse into x/y
        all_x.append(x)
        all_data.append(data_file)

    #create figure
    fig = figure()
    ax = fig.add_axes([0.13, 0.13, 0.85, 0.83])

    #style
    colors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c']  # https://colorbrewer2.org/#type=qualitative&scheme=Dark2&n=3
    lstyles = ["solid", "dotted", "dashed"]
    percentiles = [99, 95, 90, 50]
    percentiled_data = [list() for _ in range(len(percentiles))]

    #plot
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

    legend(fontsize=FONT_SIZE_LEGEND-5, bbox_to_anchor=(1.01, 1.1), ncol=4, handlelength=3, columnspacing=1)

    #save figure
    savefig(output, bbox_inches='tight')


def plot_all_ecmp_imbalance_in_cdf(csv_files, labels, xlabel, output, xlim):
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
                    data_file.extend(data)
                except Exception as e:
                    print("Exception:", e)
                    continue
        all_data.append(data_file)

    # CDF computation
    all_bins = list()
    all_cdfs = list()
    max_data = 0
    for data_file in all_data:
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
    ax.set_xlabel(latex_label(xlabel), font)

    # ax.set_xticks(list(range(0, 101, 10)))
    ax.set_xlim(xlim)

    ax.grid(True, color='gray', linestyle='dashed')

    legend(fontsize=FONT_SIZE_LEGEND-5, bbox_to_anchor=(0.95, 1.1), ncol=3, handlelength=3)

    #save figure
    savefig(output, bbox_inches='tight')
