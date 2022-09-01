use std::collections::HashMap;
use serde_yaml::{from_reader, from_str, Value};

#[derive(Debug)]
pub struct Link {
    pub label: String,
    pub load: u32,
}

#[derive(Debug)]
pub struct Router {
    pub name: String,
    pub peers: HashMap<String, Vec<Link>>,
}

fn read_yaml(filepath: &str) -> Result<HashMap<String, Router>, ()> {
    let fd = match std::fs::File::open(filepath) {
        Ok(f) => f,
        Err(e) => return Err(()), // TODO: make a custom error
    };

    let document: Value = match from_reader(fd) {
        Ok(doc) => doc,
        Err(err) => {
            println!("Error on {}: {:?}", filepath, err);
            return Err(());
        },
    };
    let mut routers: HashMap<String, Router> = HashMap::new();
    for router in document.as_mapping().unwrap() {
        let router_name = router.0.as_str().unwrap();
        let m1 = router.1.as_mapping().unwrap();
        // Create router value
        let mut r = Router {
            name: router_name.to_string(),
            peers: HashMap::new(),
        };
        for information in m1.iter() {
            let s0 = information.1.as_sequence().unwrap();
            let k_label: Value = from_str("label").unwrap();
            let k_load: Value = from_str("load").unwrap();
            let k_peer: Value = from_str("peer").unwrap();
            for link in s0 {
                let label = link.get(&k_label).unwrap().as_str().unwrap();
                let load = match link.get(&k_load) {
                    Some(val) => match val.as_u64() {
                        Some(v) => v,
                        None => {
                            println!("Parsing problem (1) with the file: {}", filepath);
                            return Err(());
                        }
                    },
                    None => {
                        println!("Parsing problem (2) with the file: {}", filepath);
                        return Err(());
                    }
                };
                let peer = match link.get(&k_peer) {
                    //p.as_str().unwrap(),
                    Some(p) => match p.as_str() {
                        Some(n) => n,
                        None => {
                            println!("Parsing problem (3) with the file: {}, {:?}", filepath, p);
                            return Err(());
                        }
                    },
                    None => {
                        println!("Parsing problem (4) with the file {}", filepath);
                        return Err(());
                    }
                };
                let link_obj = Link {
                    label: label.to_string(),
                    load: load as u32,
                };
                r.peers
                    .entry(peer.to_string())
                    .or_insert_with(Vec::new)
                    .push(link_obj);
            }
        }
        // Finally add router to the list of all routers
        routers.insert(r.name.to_owned(), r);
    }

    Ok(routers)
}
