import matplotlib.pyplot as plt
import numpy as np
import csv
from datetime import datetime


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
    

if __name__ == "__main__":
    plot_nb_evolution("../ovh-parsing/output.csv", ylabel="Nb routers evolution")