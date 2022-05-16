use chrono::NaiveDateTime;
use ovh_parsing::{parse_yaml, write_in_csv, Router};
use std::env;
use std::error::Error;

fn static_node_degree(data: &[&Router], output_csv: &str) -> Result<(), Box<dyn Error>> {
    let res = data.iter().map(|&router| router.peers.len()).collect();

    write_in_csv(res, output_csv)
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        panic!("Usage: {} <instance-path>", args[0]);
    }

    // Set a dummy timestamp, not important here
    let data = parse_yaml(&args[1], NaiveDateTime::from_timestamp(100, 0)).unwrap();
    let data_routers = data.data.iter().map(|(_, v)| v).collect::<Vec<&Router>>();
    static_node_degree(&data_routers, "../csv/static_node_degree.csv").unwrap();

    let data_external = data.get_peering_routers();
    static_node_degree(&data_external, "../csv/static_node_degree_peers.csv").unwrap();

    let data_internal = data.get_internal_routers();
    static_node_degree(&data_internal, "../csv/static_node_degree_internal.csv").unwrap();
}
