use chrono::prelude::NaiveDateTime;
use serde_yaml::{from_reader, from_str, Value};
use std::{collections::HashMap, path::Path};

#[derive(Debug)]
pub struct FileMetadata {
    pub filepath: String,
    pub timestamp: NaiveDateTime,
}

impl FileMetadata {
    pub fn path_to_file_metadata(pathbuf: &Path) -> Option<FileMetadata> {
        let timestamp_str = match pathbuf.file_name() {
            Some(filename) => match filename.to_str() {
                Some(filename_str) => filename_str,
                None => return None,
            },
            None => return None,
        }
        .split(&['_', '.'][..])
        .collect::<Vec<&str>>()[1];

        let timestamp = timestamp_str.parse::<i64>().unwrap();

        Some(FileMetadata {
            filepath: pathbuf.to_str().unwrap().to_string(),
            timestamp: NaiveDateTime::from_timestamp(timestamp, 0),
        })
    }
}

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

impl Router {
    pub fn is_external(&self) -> bool {
        self.name.to_uppercase() == self.name
    }

    pub fn get_external_links(&self) -> Option<Vec<&Vec<Link>>> {
        if self.is_external() {
            return None;
        }
        Some(self.peers.iter().filter(
            |(peer_name, _)| &&peer_name.to_uppercase() == peer_name
        ).map(|(_, links)| links).collect::<Vec<&Vec<Link>>>())
    }
}

pub struct OvhData {
    pub data: HashMap<String, Router>,
}

impl OvhData {
    pub fn get_peering_routers(&self) -> Vec<&Router> {
        self.data.iter().filter(
            |(_, router)| router.is_external()
        ).map(|(_, router)| router)
        .collect::<Vec<&Router>>()
    }

    pub fn get_internal_routers(&self) -> Vec<&Router> {
        self.data.iter().filter(
            |(_, router)| !router.is_external()
        ).map(|(_, router)| router)
        .collect::<Vec<&Router>>()
    }
}

/// TODO: this function needs to be refactored, because it uses
/// my *very few* skills in Rust
pub fn parse_yaml(filepath: &str) -> OvhData {
    let fd = std::fs::File::open(filepath).unwrap();
    let document: Value = from_reader(fd).unwrap();
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
                let load = link.get(&k_load).unwrap().as_u64().unwrap();
                let peer = match link.get(&k_peer) {
                    //p.as_str().unwrap(),
                    Some(p) => match p.as_str() {
                        Some(n) => n,
                        None => {
                            println!("Does not work: {}, {:?}", filepath, p);
                            panic!("Error");
                        }
                    },
                    None => {
                        println!("Error in file {}", filepath);
                        panic!("Problem");
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
    OvhData {data: routers}
}
