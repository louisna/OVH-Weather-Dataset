import csv
import sys
import datetime


def read_data(filename: str) -> dict[(str, str), list[int]]:
    data_dict = dict()
    with open(filename) as fd:
        for row in csv.reader(fd):
            data_dict.setdefault((row[1], row[2]), list()).append(int(row[0]))
    return data_dict


def filter_data(data: dict[(str, str), list[int]]):
    # Consider that data with timestamps closer than 1 hour are in the same "time window"
    data_filtered = list()
    for (r_a, r_b), timestamp_vec in data.items():
        idx_first = 0
        idx_runner = 1
        while idx_runner < len(timestamp_vec):
            t_1 = datetime.datetime.fromtimestamp(timestamp_vec[idx_runner - 1])
            t_2 = datetime.datetime.fromtimestamp(timestamp_vec[idx_runner])
            if (t_2 - t_1).total_seconds() / 3600 > 1:
                data_filtered.append((r_a, r_b, timestamp_vec[idx_first]))
                idx_first = idx_runner
            idx_runner += 1
        data_filtered.append((r_a, r_b, timestamp_vec[idx_first]))
    return data_filtered


def dump_data(data: list[(str, str, int)], output_filename: str):
    with open(output_filename, "w+") as fd:
        wrt = csv.writer(fd)
        wrt.writerows(data)


if __name__ == "__main__":
    data = read_data(sys.argv[1])
    print(data)
    data_filtered = filter_data(data)
    dump_data(data_filtered, "high_loads_filtered.csv")