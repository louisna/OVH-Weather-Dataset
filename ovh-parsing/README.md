# Usage

Example of data parsing :

```bash
cargo run --release --  <path-to-yaml-dir> -u day -s 1 -t nb-links -o nb-links.csv
```

This will save in a `nb-links.csv` file (in CSV format) the evolution of the number of links of the files in the `<path-to-yaml-dir>` directory.

It will sample a single file (`-s 1`) each day (`-u day`), starting from the first file in the yaml directory, and computes the total number of links in the selected sample.

The CSV output file has the following format:
* First row: each selected timestamp value (i64)
* Second row: for the timestamp instance (at the same column index), the number of links computed from the yaml.