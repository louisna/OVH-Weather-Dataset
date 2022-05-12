use chrono::prelude::NaiveDateTime;
use csv::{WriterBuilder, Writer};
use std::fs::File;
use serde::Serialize;
use serde_yaml::{from_reader, from_str, Value};
use std::error::Error;
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

pub fn write_in_csv<T: Serialize>(values: Vec<T>, filepath: &str) -> Result<(), Box<dyn Error>> {
    let mut wrt = WriterBuilder::new()
        .has_headers(false)
        .from_path(filepath)?;

    for value in values {
        wrt.serialize(value)?;
    }

    Ok(())
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

    pub fn has_external(&self) -> bool {
        self.peers
            .iter()
            .map(|(peer_name, _)| &peer_name.to_uppercase() == peer_name)
            .any(|x| x)
    }

    pub fn get_external_links(&self) -> Option<Vec<&Vec<Link>>> {
        if self.is_external() {
            return None;
        }
        Some(
            self.peers
                .iter()
                .filter(|(peer_name, _)| &&peer_name.to_uppercase() == peer_name)
                .map(|(_, links)| links)
                .collect::<Vec<&Vec<Link>>>(),
        )
    }

    pub fn get_nb_links(&self) -> i32 {
        self.peers.values().map(|v| v.len() as i32).sum::<i32>()
    }

    pub fn get_links_load_with(&self, other: &str) -> Option<Vec<u32>> {
        self.peers
            .get(other)
            .map(|peer| peer.iter().map(|link| link.load).collect())
    }
}

pub struct ExperimentResults {
    pub timestamp: NaiveDateTime,
    pub nb_nodes: i32,
    pub nb_links: i32,
}

impl ExperimentResults {
    pub fn write_csv_nb_nodes(&self, wrt: &mut Writer<File>) -> Result<(), csv::Error> {
        wrt.serialize((&self.timestamp.timestamp(), self.nb_nodes))
    }

    pub fn write_csv_nb_links(&self, wrt: &mut Writer<File>) -> Result<(), csv::Error> {
        wrt.serialize((&self.timestamp.timestamp(), self.nb_links))
    }
}

pub struct OvhData {
    pub timestamp: NaiveDateTime,
    pub data: HashMap<String, Router>,
}

impl OvhData {
    pub fn get_peering_routers(&self) -> Vec<&Router> {
        self.data
            .iter()
            .filter(|(_, router)| router.is_external())
            .map(|(_, router)| router)
            .collect::<Vec<&Router>>()
    }

    pub fn get_internal_routers(&self) -> Vec<&Router> {
        self.data
            .iter()
            .filter(|(_, router)| !router.is_external())
            .map(|(_, router)| router)
            .collect::<Vec<&Router>>()
    }

    pub fn get_border_routers(&self) -> Vec<&Router> {
        self.data
            .iter()
            .filter(|(_, router)| router.has_external())
            .map(|(_, router)| router)
            .collect()
    }

    pub fn get_router_links_load_with(
        &self,
        router_name: &str,
        peer_name: &str,
    ) -> Option<Vec<u32>> {
        match self.data.get(router_name) {
            Some(router) => router.get_links_load_with(peer_name),
            None => None,
        }
    }

    pub fn get_nb_nodes(&self) -> i32 {
        self.data.len() as i32
    }

    pub fn get_nb_links(&self) -> i32 {
        (self.data
            .values()
            .map(|router| {
                router
                    .peers
                    .values()
                    .map(|peering| peering.len())
                    .sum::<usize>()
            })
            .sum::<usize>()
            / 2) as i32
    }
}

/// TODO: this function needs to be refactored, because it uses
/// my *very few* skills in Rust
pub fn parse_yaml(filepath: &str, timestamp: NaiveDateTime) -> Option<OvhData> {
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
                let load = match link.get(&k_load) {
                    Some(val) => match val.as_u64() {
                        Some(v) => v,
                        None => {
                            println!("Voici l'autre fichier qui pose probleme: {}", filepath);
                            return None;
                        }
                    },
                    None => {
                        println!("Voici le fichier qui merde: {}", filepath);
                        return None;
                    }
                };
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
    Some(OvhData {
        data: routers,
        timestamp,
    })
}
