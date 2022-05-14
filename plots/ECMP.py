"""
Plots OVH ECMP

__author__  = "Benoit Donnet (ULiege -- Institut Montefiore)"
__version__ = "1.0"
__date__    = "14/05/2022"
"""

from Utils_Benoit import *
from matplotlib.colors import LogNorm, Normalize

empty_date_label=["","","","","","","","","","","","","","","","","","","","","","","","",""]

def plot_ecmp_imbalance(values, total, output,figsize_x=24, figsize_y=15, cbar_center=0.1, max_ylim_total=3000000):
    """
    Plots ECMP imbalance in OVH through heatmap

    Args:
        values: imbalance values on a per month basis
        total: total of imbalance values on a per month basis
        output: output filename
        figsize_x: figure width (24 by default)
        figsize_y: figure height (15 by default)
        cbar_center: color bar center point (0.1 by default)
        max_ylim_total: max Y axis value for the below bar plot (3000000 by default)
    """
    #load data
    dfValues = pd.read_csv(values, sep=';', skipinitialspace=True, parse_dates=['Time'])
    dfTotal  = pd.read_csv(total, sep=';', skipinitialspace=True, parse_dates=['Time'])

    #computes relative values
    dfValues = dfValues[['[0,1[','[1,2[','[2,3[','[3,4[','[4,5[','[5,6[','[6,7[','[7,100[']]
    dfValues.loc[:,'[0,1[':'[7,100['] = dfValues.loc[:,'[0,1[':'[7,100['].div(dfValues.sum(axis=1), axis=0)

    #create subfigures
    f, ax = plt.subplots(2,1,figsize=(figsize_x,figsize_y))

    #global style
    sns.set(style="ticks",context="paper", color_codes=True, font_scale=2, font=font)

    ###########################
    # HeatMap                 #
    ###########################
    df = dfValues.transpose()

    midnorm = MidpointNormalize(vmin=0, vcenter=cbar_center, vmax=np.nanmax(df))
    df.replace(0, np.nan, inplace=True)
    mask = df.isnull()

    g = sns.heatmap(df, cbar_kws={'label': latex_label('Proportion'), "use_gridspec" : False,
                    "location":"top", "extend":"both", 'anchor':(0.2,0.2)},
                     xticklabels=empty_date_label, #yticklabels=yticklabels_heatmap,
                     norm=midnorm, cmap='coolwarm', annot=False, ax=ax[0], mask=mask)#, vmin=1, vmax=np.nanmax(df))

    g.set_ylabel(latex_label('ECMP Imbalance'), fontsize=FONT_SIZE)
    sns.despine(offset=10, top=True, right=True, left=False, bottom=False)

    # Color bar and size of ticks
    g.figure.axes[-1].xaxis.label.set_size(FONT_SIZE)
    g.collections[0].colorbar.ax.tick_params(labelsize=FONT_SIZE_TICKS)

    ax[0].tick_params(axis='both', which='major', labelsize=FONT_SIZE_TICKS)
    ax[0].tick_params(direction='inout', length=4, width=2)

    ###########################
    # BarPlot                 #
    ###########################
    dfTotal.plot(y='Total', kind='bar', legend=False, ax=ax[1])
    ax[1].semilogy()
    ax[1].set_ylim(1, max_ylim_total)

    axis_aesthetic(ax[1])
    #ax[1].set_xticklabels(date_labels, rotation=45, horizontalalignment='center', fontsize=FONT_SIZE_TICKS)
    ax[1].set_xlabel(latex_label('Time'), font)
    ax[1].set_ylabel(latex_label("Raw Number"), font)
    ax[1].tick_params(axis='both', which='major', labelsize=FONT_SIZE_TICKS)

    ax[1].grid(True, color='gray', linestyle='dashed')

    savefig(output, bbox_inches='tight')
