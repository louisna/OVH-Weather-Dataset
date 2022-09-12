# OVH Weather dataset

This repository contains all the parsing files and wrapping scripts used for the OVH Weather dataset. It is linked to the paper _Revealing the Evolution of a Cloud Provider Through its Network Weather Map_, accepted at the _Internet Measure Conference 2022 (IMC'22)_.

Additionally, the repository includes all the analysis scripts used to generate the plots from the paper, as well as scripts to read the YAML files.

## SVG parsing scripts

We provide the [weathermap_parse.py](weathermap_parse.py) Python script. This script reads SVG files from a directory and parses them in a user-friendly YAML format. As explained in the paper, several sanity checks are performed to ensure that the SVG->YAML translation is correct.

To parse the OVH weather map SVG files from a directory, one can use the parsing script as follows.

```bash
weathermap_parse.py <path-to-directory>
```

This will parse all files from the directory given as argument. The YAML files are located in a new directory `<path-to-directory>_yaml`. For example, if the argument is `~/SomeUser/SomeOVHData`, the parsed YAML files will be located in `~/SomeUser/SomeOVHData_yaml`.

## Read YAML files

The YAML parsed files can be loaded in memory for further analysis. As a starting point, we implemented YAML readers for the OVH Weather dataset in the following languages (available in the [yaml_readers](yaml_readers/) directory):
- [Rust](yaml_readers/rust/src/lib.rs)
- [Python](yaml_readers/python/read_yaml.py)

Any contribution to extend this list is welcomed.

## Analysing scripts from the paper

TODO

## Cite this paper

TODO

## Copyright

Louis Navarre, UCLouvain. September, 2022.
