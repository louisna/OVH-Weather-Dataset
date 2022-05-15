# Generation of data from this directory

The following command generates the results for March 2022 only.

```bash
$ cargo run --bin ovh-parsing --release -- /mnt/traces/ovh/data_yaml -u all -s 1 -n 20 -o ../csv_march_2022/ --start-timestamp 1646089212 --stop-timestamp 1648763709
```