use chrono::NaiveDateTime;
use core::panic;
use ovh_parsing::{parse_yaml, OvhData, OvhNodeFilter, Router};
use std::{collections::HashMap, env};

fn try_and_connect_network(
    europe: OvhData,
    america: OvhData,
    asia: OvhData,
    world_data: OvhData,
) -> Option<OvhData> {
    let mut total: HashMap<String, Router> = HashMap::new();
    let timestamp = europe.timestamp;

    let maps = [europe, america, asia, world_data]; // Give ownership

    for map in maps {
        for (router_name, router) in map.data {
            // Consume the values
            if let std::collections::hash_map::Entry::Vacant(e) =
                total.entry(router_name.to_string())
            {
                e.insert(router);
            } else {
                let router_exists = total.get_mut(&router_name).unwrap();
                for (peer_name, peer_links) in router.peers {
                    if router_exists.peers.contains_key(&peer_name) {
                        if router_exists.peers.get(&peer_name).unwrap().len() < peer_links.len() {
                            let peer_links_length = peer_links.len();
                            println!(
                                "{} -> {}: {} >< {}",
                                &router_name,
                                &peer_name,
                                router_exists.peers.get(&peer_name).unwrap().len(),
                                peer_links.len()
                            );
                            router_exists
                                .peers
                                .insert(peer_name.to_string(), peer_links); // Exchange
                                                                            // Ensure that we correctly exchanged it
                            assert_eq!(
                                router_exists.peers.get(&peer_name).unwrap().len(),
                                peer_links_length
                            );
                            // Assume the maximum of both is the most probable => exchange the links
                        } // Else: either we already have the maximum, or they are equivalent
                    } else {
                        // The router exists, but we do not have the connections yet with the peer
                        router_exists.peers.insert(peer_name, peer_links);
                    }
                }
            }
        }
    }

    Some(OvhData {
        timestamp,
        data: total,
    })
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 4 {
        panic!(
            "Usage: {} <Europe> <America> <Asia-Pacific> <World>",
            args[0]
        );
    }

    let europe_data = parse_yaml(&args[1], NaiveDateTime::from_timestamp(100, 100)).unwrap();
    let america_data = parse_yaml(&args[2], NaiveDateTime::from_timestamp(100, 100)).unwrap();
    let asia_data = parse_yaml(&args[3], NaiveDateTime::from_timestamp(100, 100)).unwrap();
    let world_data = parse_yaml(&args[4], NaiveDateTime::from_timestamp(100, 100)).unwrap();

    println!(
        "Europe number of links: {}",
        europe_data.get_nb_links(OvhNodeFilter::All)
    );
    println!(
        "Europe number of OVH links: {}",
        europe_data.get_nb_links(OvhNodeFilter::Ovh)
    );
    println!(
        "Europe number of external links: {}",
        europe_data.get_nb_links(OvhNodeFilter::External)
    );

    println!(
        "Europe number of nodes: {}",
        europe_data.get_nb_nodes(OvhNodeFilter::All)
    );
    println!(
        "Europe number of OVH nodes: {}",
        europe_data.get_nb_nodes(OvhNodeFilter::Ovh)
    );
    println!(
        "Europe number of external nodes: {}",
        europe_data.get_nb_nodes(OvhNodeFilter::External)
    );
    println!();

    println!(
        "America number of links: {}",
        america_data.get_nb_links(OvhNodeFilter::All)
    );
    println!(
        "America number of OVH links: {}",
        america_data.get_nb_links(OvhNodeFilter::Ovh)
    );
    println!(
        "America number of external links: {}",
        america_data.get_nb_links(OvhNodeFilter::External)
    );

    println!(
        "America number of nodes: {}",
        america_data.get_nb_nodes(OvhNodeFilter::All)
    );
    println!(
        "America number of OVH nodes: {}",
        america_data.get_nb_nodes(OvhNodeFilter::Ovh)
    );
    println!(
        "America number of external nodes: {}",
        america_data.get_nb_nodes(OvhNodeFilter::External)
    );
    println!();

    println!(
        "Asia number of links: {}",
        asia_data.get_nb_links(OvhNodeFilter::All)
    );
    println!(
        "Asia number of OVH links: {}",
        asia_data.get_nb_links(OvhNodeFilter::Ovh)
    );
    println!(
        "Asia number of external links: {}",
        asia_data.get_nb_links(OvhNodeFilter::External)
    );

    println!(
        "Asia number of nodes: {}",
        asia_data.get_nb_nodes(OvhNodeFilter::All)
    );
    println!(
        "Asia number of OVH nodes: {}",
        asia_data.get_nb_nodes(OvhNodeFilter::Ovh)
    );
    println!(
        "Asia number of external nodes: {}",
        asia_data.get_nb_nodes(OvhNodeFilter::External)
    );
    println!();

    println!(
        "World number of links: {}",
        world_data.get_nb_links(OvhNodeFilter::All)
    );
    println!(
        "World number of OVH links: {}",
        world_data.get_nb_links(OvhNodeFilter::Ovh)
    );
    println!(
        "World number of external links: {}",
        world_data.get_nb_links(OvhNodeFilter::External)
    );

    println!(
        "World number of nodes: {}",
        world_data.get_nb_nodes(OvhNodeFilter::All)
    );
    println!(
        "World number of OVH nodes: {}",
        world_data.get_nb_nodes(OvhNodeFilter::Ovh)
    );
    println!(
        "World number of external nodes: {}",
        world_data.get_nb_nodes(OvhNodeFilter::External)
    );
    println!();

    let total = match try_and_connect_network(europe_data, america_data, asia_data, world_data) {
        None => panic!("Impossible to parse the maps together."),
        Some(total) => total,
    };

    // Do whatever you want with the data
    println!(
        "Total number of nodes: {}",
        total.get_nb_nodes(OvhNodeFilter::All)
    );
    println!(
        "Total number of OVH nodes: {}",
        total.get_nb_nodes(OvhNodeFilter::Ovh)
    );
    println!(
        "Total number of external nodes: {}",
        total.get_nb_nodes(OvhNodeFilter::External)
    );

    println!(
        "Total number of links: {}",
        total.get_nb_links(OvhNodeFilter::All)
    );
    println!(
        "Total number of OVH links: {}",
        total.get_nb_links(OvhNodeFilter::Ovh)
    );
    println!(
        "Total number of external links: {}",
        total.get_nb_links(OvhNodeFilter::External)
    );
}
