#! /usr/bin/python3

import csv
import time

import matplotlib.pyplot as plt

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
