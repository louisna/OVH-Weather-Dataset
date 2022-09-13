use chrono::NaiveDateTime;
use ovh_parsing::{parse_yaml, write_in_csv, Link, OvhData, OvhNodeFilter, Router};
use std::env;
use std::error::Error;

fn _static_node_degree(data: &[&Router], output_csv: &str) -> Result<(), Box<dyn Error>> {
    let res = data.iter().map(|&router| router.peers.len()).collect();

    write_in_csv(res, output_csv)
}

fn static_node_degree_with_ecmp(data: &[&Router], output_csv: &str) -> Result<(), Box<dyn Error>> {
    let res: Vec<i32> = data
        .iter()
        .map(|&router| router.peers.values().fold(0, |s, l| s + l.len() as i32))
        .collect();

    write_in_csv(res, output_csv)
}

fn static_nb_ecmp_links_mean(data: &[&Router]) -> f64 {
    let (a, b) = data.iter().fold((0i32, 0i32), |(sum, nb), router| {
        let ecmp: Vec<Vec<&Link>> = router
            .peers
            .values()
            .map(|links| links.iter().filter(|link| link.load > 1).collect())
            .filter(|links: &Vec<&Link>| links.len() > 1)
            .collect();
        let s2 = ecmp.iter().fold(0, |s, v| s + v.len()) as i32;
        (sum + s2, nb + ecmp.len() as i32)
    });
    a as f64 / b as f64
}

fn static_nb_ecmp_total_mean(data: &OvhData) -> f64 {
    data.get_nb_links(OvhNodeFilter::Ovh) as f64 / data.get_nb_nodes(OvhNodeFilter::Ovh) as f64
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        panic!("Usage: {} <instance-path>", args[0]);
    }

    // Set a dummy timestamp, not important here
    let data = parse_yaml(&args[1], NaiveDateTime::from_timestamp(100, 0)).unwrap();
    let data_routers = data.data.iter().map(|(_, v)| v).collect::<Vec<&Router>>();
    static_node_degree_with_ecmp(&data_routers, "../csv/static_node_degree.csv").unwrap();

    let data_external = data.get_peering_routers();
    static_node_degree_with_ecmp(&data_external, "../csv/static_node_degree_peers.csv").unwrap();

    let data_internal = data.get_internal_routers();
    static_node_degree_with_ecmp(&data_internal, "../csv/static_node_degree_internal.csv").unwrap();

    println!(
        "Mean number of links per ECMP: {}",
        static_nb_ecmp_links_mean(&data_internal)
    );
    println!(
        "Mean number of links per ECMP without filtering: {}",
        static_nb_ecmp_total_mean(&data)
    );
}
