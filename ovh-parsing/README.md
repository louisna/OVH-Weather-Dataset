# Analysis

This directory contains the processing code used for the analysis of the OVH network, as detailed in the paper. This analysis is kept simple, to show the potential of the data.

This directory contains several files.

## Main parsing: [`main.rs`](src/main.rs)

The [`main.rs`](src/main.rs) file reads the YAML files (the path to these files is a required argument) and outputs several CSV and YAML files:

- `nb-nodes-<all,ovh,external>.csv`: Evolution of the number of nodes (all, only OVH routers, only peering routers),
- `nb-links-<all,ovh,external>.csv`: Evolution of the number of links (all, only OVH routers, only peering routers),
- `ecmp-diffs-<all,ovh,external>.yaml`: The load percentage difference for each outgoing node (all, ony OVH routers, only peering routers) for each snapshot,
- `loads-<all,ovh,external>.yaml` (**only if the `enable-full-load` argument is set**): The loads of all links for all snapshots (all, only OVH routers, only peering routers).

### Usage

```
cargo run --release --bin ovh-parsing -- -n <nb threads> --enable-full-load -o <path to output dir> <path to input dir>
```

### Sampling

It is also possible to choose a sampling of values, instead of loading all data. The full help is available:

```
USAGE:
    ovh-parsing [FLAGS] [OPTIONS] <directory-path>

FLAGS:
        --enable-full-load    If set, store non-aggregated results about ECMP diffs and link loads in YAML files
    -h, --help                Prints help information
    -V, --version             Prints version information

OPTIONS:
    -n <nb-threads>                                     Number of threads used to parse the yaml files [default: 4]
    -o <output-dir>
            Output directory where all the CSV results files will be stored [default: .]

        --start-timestamp <start-specific-timestamp>    Start the parsing at the very specified timestamp
    -s <step>                                           Step value to skip files with unit `unit_step` [default: 1]
        --stop-timestamp <stop-timestamp>               Stop the parsing at the very specified timestamp
    -u <unit-step>
            The unit of time we use for the steps. Default "all" considers all files [default: all]  [possible values:
            all, hour, day]

ARGS:
    <directory-path>    Directory containing the input yamls
```

## Static analysis on a single snapshot: [`static_analysis.rs`](src/bin/static_analysis.rs)

This binary file makes static analysis on a single snapshot of the OVH (European) network. It outputs the following CSV files:

- `static_node_degree.csv`: The node degree of each router of the network,
- `static_node_degree_peers.csv`: The node degree of each peering router of the network,
- `static_node_degree_internal.csv`: The node degree of each OVH router of the network.

Additionally, it prints the mean number of ECMP links of the OVH routers and without any distinction.

### Usage

```bash
cargo run --release --bin static_analysis -- <Europe map file>
```

## Link all the maps together: [`link_world.rs`](src/bin/link_world.rs)

This binary file takes as input the 4 different maps and tries to link them together, to create the global OVH backbone network. This is a simple example of how one can leverage the redundant information from the YAML files to make a more general analysis of the OVH network evolution.

### Usage

```bash
cargo run --release --bin link_world -- <Europe map file> <America map file> <APAC map file> <World map file>
```