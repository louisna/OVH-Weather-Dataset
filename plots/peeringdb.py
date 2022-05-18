import csv
import time
import matplotlib.pyplot as plt
from Utils_Benoit import *
"""
i = 211
for peering in ["AMS-IX_ams-1-n7", "AMS-IX_ams-5-n7"]:
    ax = plt.subplot(i)
    with open("../csv/%s.csv" % peering) as fd:
        first = True
        for row in csv.reader(fd):
            if first:
                header = [float(i) for i in row[2:]]
                first = False
                continue

            if row[0] == "up":
                data = [int(i) for i in row[2:]]
                print(row[1])
                try:
                    ax.plot(header, data, label=row[1])
                except ValueError as e:
                    print("Failures for %s\n%s" % (row[1], e))
                if data[0] == -1:
                    addition = True
                    for idx, value in enumerate(data):
                        if value != -1 and idx != header[-1] and addition:
                            ax.vlines(header[idx], 0, 100, colors=['r'], linestyles='dashed')
                            ax.annotate('Link addition',
                                xy=(header[idx],75),
                                xycoords='data',
                                xytext=(0.30, 0.95),
                                textcoords='axes fraction',
                                arrowprops=dict(facecolor='black', shrink=0.05),
                                horizontalalignment='right',
                                verticalalignment='top',
                            )
                            addition = False
                        elif value != -1 and idx != header[-1] and value != 0:
                            ax.annotate('Link activation',
                                xy=(header[idx],5),
                                xycoords='data',
                                xytext=(0.3 if i == 211 else 0.6, 0.2),
                                textcoords='axes fraction',
                                arrowprops=dict(facecolor='black', shrink=0.05),
                                horizontalalignment='right',
                                verticalalignment='top',
                            )
                            break


    peeringdb = 1646970358.0
    ax.vlines(peeringdb, 0, 100, colors=['r'])
    ax.annotate('PeeringDB update',
            xy=(peeringdb,75),
            xycoords='data',
            xytext=(0.45, 0.95),
            textcoords='axes fraction',
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='right',
            verticalalignment='top',
    )
    plt.axis([header[0], header[len(header)-1], 0, 100])
    plt.legend()
    if i == 211:
        ax.title.set_text("Upload link load from OVH backbone to AMS-IX")
        ax.xaxis.set_visible(False)
    else:
        ax.set_xlabel("Time")

        l = len(header)
        idx = [0, int(l/4), int(l/2), int(l*3/4), l-1]
        print(idx)
        vals = [header[i] for i in idx]
        ax.set_xticks(vals, [time.strftime("%Y-%m-%d\n%H:%M:%S", time.gmtime(i)) for i in vals])
    ax.set_ylabel("Links load [%]")

    i+=1

plt.savefig("../figures/peering.pdf")
plt.show()
"""


def plot_peering_db_example(csv_files, output):
    all_data_up = list()
    all_data_down = list()
    all_x = list()

    for file in csv_files:
        data_file_up = list()
        data_file_down = list()
        x = list()


        with open(file) as fd:
            first = True
            for row in csv.reader(fd):
                if first:
                    x = [datetime.fromtimestamp(int(i)) for i in row[2:]]
                    first = False
                    continue
                # Data rows
                up_down = row[0]
                label = row[1]
                load = [int(i) for i in row[2:]]
                if up_down == "up":
                    data_file_up.append((label, load))
                else:
                    data_file_down.append((label, load))
        all_data_up.append(data_file_up)
        all_data_down.append(data_file_down)
        all_x.append(x)

    fig = figure(figsize=(9, 4.0))
    ax = fig.add_axes([0.13, 0.13, 0.85, 0.83])

    # Assume there is only one file
    # Only care about uplink load
    all_data_up[0] = sorted(all_data_up[0])
    colors = ['#1b9e77', '#d95f02', '#66a61e', '#e7298a', '#7570b3']
    for i, values in enumerate(all_data_up[0]):
        # Is it the link we look for ? i.e., that has been added...
        if -1 in values[1]:
            tmp = [i for i in values[1] if i >= 0]
            x_values = all_x[0][-len(tmp):]
            # Plot the moment when the link has been added
            idx_first_0 = x_values[0]
            ax.vlines([idx_first_0], -10, 100, colors=["red"], linestyle="dashed", linewidth=3)
            ax.annotate('A',
                                xy=([datetime.fromtimestamp(idx_first_0.timestamp() - 10000)],15),
                                xycoords='data',
                                xytext=(0.15, 0.15),
                                textcoords='axes fraction',
                                arrowprops=dict(facecolor='black', shrink=0.05, width=0.75, headwidth=7),
                                horizontalalignment='right',
                                verticalalignment='top',
                                fontsize=20
                            )
            # Plot the moment when the link is activated
            # We do not plot finally
            i_first_1 = tmp.index(1)
            idx_first_1 = x_values[i_first_1]
            # ax.vlines([idx_first_1], -10, 100, colors=["red"], linestyle="dashed")
            ax.annotate('C',
                                xy=([datetime.fromtimestamp(idx_first_1.timestamp() + 10000)],15),
                                xycoords='data',
                                xytext=(0.59, 0.15),
                                textcoords='axes fraction',
                                arrowprops=dict(facecolor='black', shrink=0.09, width=0.75, headwidth=7),
                                horizontalalignment='left',
                                verticalalignment='top',
                                fontsize=20
                            )

            # Plot the link load
            ax.plot(x_values, tmp, label=f"\#{values[0][-1]}", color=colors[i], linewidth=4)

        else:
            ax.plot(all_x[0], values[1], label=f"\#{values[0][-1]}", color=colors[i])

    peeringdb = 1646970358
    peering_dt = datetime.fromtimestamp(peeringdb)
    ax.vlines(peering_dt, 0, 100, colors=['r'], linewidth=3)
    ax.annotate('B',
            xy=(datetime.fromtimestamp(peeringdb - 10000),15),
            xycoords='data',
            xytext=(0.4, 0.15),
            textcoords='axes fraction',
            arrowprops=dict(facecolor='black', shrink=0.05, width=0.75, headwidth=7),
            horizontalalignment='right',
            verticalalignment='top',
            fontsize=20
    )

    axis_aesthetic(ax)
    ax.set_ylabel(latex_label("Load (\%)"), font)
    ax.set_xlabel(latex_label('Time'), font)
    myFmt = mdates.DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(myFmt)
    fig.autofmt_xdate(ha="center")

    # ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_yticks(list(range(0, 71, 10)))

    ax.grid(True, color='gray', linestyle='dashed')
    ylim(-1, 70)

    # Change legend order to show in last the added link
    handles, labels = plt.gca().get_legend_handles_labels()
    order = list(range(1, len(all_data_up[0]))) + [0]


    legend([handles[idx] for idx in order],[labels[idx] for idx in order], fontsize=FONT_SIZE_LEGEND, bbox_to_anchor=(0.95, 1.2), ncol=5, handlelength=2, columnspacing=1)
    savefig(output, bbox_inches='tight')
