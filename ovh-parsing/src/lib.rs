use chrono::prelude::NaiveDateTime;
use std::{
    path::Path, collections::HashMap,
};
use serde_yaml::{from_reader, Value, from_str};

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
    label: String,
    load: u32,
}

#[derive(Debug)]
pub struct Router {
    name: String,
    peers: HashMap<String, Vec<Link>>,
}

/// TODO: this function needs to be refactored, because it uses
/// my *very few* skills in Rust
pub fn parse_yaml(filepath: &str) -> Vec<Router> {
    let fd = std::fs::File::open(filepath).unwrap();
    let document: Value = from_reader(fd).unwrap();
    let mut routers: Vec<Router> = Vec::new();
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
                let peer = match link.get(&k_peer) {  //p.as_str().unwrap(),
                    Some(p) => match p.as_str() {
                        Some(n) => n,
                        None => {
                            println!("Does not work: {}, {:?}", filepath, p);
                            panic!("Error");
                        }
                    }
                    None => {
                        println!("Error in file {}", filepath);
                        panic!("Problem");
                    }
                };
                let link_obj = Link { label: label.to_string(), load: load as u32 };
                r.peers.entry(peer.to_string()).or_insert_with(Vec::new).push(link_obj);
            }
        }
        // Finally add router to the list of all routers
        routers.push(r);
    }
    routers
}