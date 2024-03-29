// Author: Louis Navarre <louis.navarre@uclouvain.be> (UCLouvain -- INL)
// Date: 10/05/2022

use chrono::prelude::{NaiveDate, NaiveDateTime, NaiveTime};
use chrono::Datelike;
use csv::{Writer, WriterBuilder};
use serde::Serialize;
use serde_json::to_string as json_to_string;
use serde_yaml::{from_reader, from_str, Value};
use std::error::Error;
use std::fs::File;
use std::io::Write;
use std::{cmp, collections::HashMap, path::Path};
pub mod get_files;

#[derive(Debug)]
pub struct FileMetadata {
    pub filepath: String,
    pub timestamp: NaiveDateTime,
}

pub enum OvhNodeFilter {
    All,
    Ovh,
    External,
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

        let timestamp = match timestamp_str.parse::<i64>() {
            Ok(t) => t,
            Err(_) => return None,
        };

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

fn is_peer_from_name(name: &str) -> bool {
    let str_split: Vec<&str> = name.split('#').collect();
    str_split[0].to_uppercase() == str_split[0]
}

#[derive(Debug, Serialize, Clone)]
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
        is_peer_from_name(&self.name)
    }

    pub fn has_external(&self) -> bool {
        self.peers
            .iter()
            .map(|(peer_name, _)| is_peer_from_name(peer_name))
            .any(|x| x)
    }

    pub fn get_external_links(&self) -> Option<Vec<&Vec<Link>>> {
        if self.is_external() {
            return None;
        }
        Some(
            self.peers
                .iter()
                .filter(|(peer_name, _)| is_peer_from_name(peer_name))
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

#[derive(Debug)]
pub struct ExperimentResults {
    pub timestamp: NaiveDateTime,

    pub nb_nodes: i32,
    pub nb_nodes_ovh: i32,
    pub nb_nodes_external: i32,

    pub nb_links: i32,
    pub nb_links_ovh: i32,
    pub nb_links_external: i32,

    pub ecmp_diffs: Vec<i8>,
    pub ecmp_diffs_ovh: Vec<i8>,
    pub ecmp_diffs_external: Vec<i8>,

    pub loads: Vec<i8>,
    pub loads_ovh: Vec<i8>,
    pub loads_external: Vec<i8>,

    pub nb_ecmp_links: Vec<i8>,
    pub nb_ecmp_links_ovh: Vec<i8>,
    pub nb_ecmp_links_external: Vec<i8>,
}

impl Default for ExperimentResults {
    fn default() -> ExperimentResults {
        ExperimentResults {
            timestamp: NaiveDateTime::from_timestamp(0, 0),
            nb_nodes: 0,
            nb_nodes_ovh: 0,
            nb_nodes_external: 0,
            nb_links: 0,
            nb_links_ovh: 0,
            nb_links_external: 0,
            ecmp_diffs: Vec::new(),
            ecmp_diffs_ovh: Vec::new(),
            ecmp_diffs_external: Vec::new(),
            nb_ecmp_links: Vec::new(),
            nb_ecmp_links_ovh: Vec::new(),
            nb_ecmp_links_external: Vec::new(),
            loads: Vec::new(),
            loads_ovh: Vec::new(),
            loads_external: Vec::new(),
        }
    }
}

impl ExperimentResults {
    pub fn write_csv_nb_nodes(
        &self,
        wrt: &mut Writer<File>,
        ovh_nodes: OvhNodeFilter,
    ) -> Result<(), csv::Error> {
        wrt.serialize((
            &self.timestamp.timestamp(),
            match ovh_nodes {
                OvhNodeFilter::Ovh => self.nb_nodes_ovh,
                OvhNodeFilter::External => self.nb_nodes_external,
                OvhNodeFilter::All => self.nb_nodes,
            },
        ))
    }

    pub fn write_csv_nb_links(
        &self,
        wrt: &mut Writer<File>,
        ovh_nodes: OvhNodeFilter,
    ) -> Result<(), csv::Error> {
        wrt.serialize((
            &self.timestamp.timestamp(),
            match ovh_nodes {
                OvhNodeFilter::Ovh => self.nb_links_ovh,
                OvhNodeFilter::External => self.nb_links_external,
                OvhNodeFilter::All => self.nb_links,
            },
        ))
    }

    pub fn write_yaml_ecmp_diff(
        &self,
        file_wrt: &mut File,
        ovh_nodes: OvhNodeFilter,
    ) -> Result<(), std::io::Error> {
        let ecmp_values = match ovh_nodes {
            OvhNodeFilter::Ovh => &self.ecmp_diffs_ovh,
            OvhNodeFilter::External => &self.ecmp_diffs_external,
            OvhNodeFilter::All => &self.ecmp_diffs,
        };
        let j_value = json_to_string(ecmp_values).unwrap();
        let j_key = json_to_string(&self.timestamp.timestamp()).unwrap();

        writeln!(file_wrt, "{}: {}", j_key, j_value)
    }

    pub fn write_yaml_nb_ecmp_links(
        &self,
        file_wrt: &mut File,
        ovh_nodes: OvhNodeFilter,
    ) -> Result<(), std::io::Error> {
        let ecmp_values = match ovh_nodes {
            OvhNodeFilter::Ovh => &self.nb_ecmp_links_ovh,
            OvhNodeFilter::External => &self.nb_ecmp_links_external,
            OvhNodeFilter::All => &self.nb_ecmp_links,
        };
        let j_value = json_to_string(ecmp_values).unwrap();
        let j_key = json_to_string(&self.timestamp.timestamp()).unwrap();

        writeln!(file_wrt, "{}: {}", j_key, j_value)
    }

    pub fn write_yaml_load(
        &self,
        file_wrt: &mut File,
        ovh_nodes: OvhNodeFilter,
    ) -> Result<(), std::io::Error> {
        let ecmp_values = match ovh_nodes {
            OvhNodeFilter::Ovh => &self.loads_ovh,
            OvhNodeFilter::External => &self.loads_external,
            OvhNodeFilter::All => &self.loads,
        };
        let j_value = json_to_string(ecmp_values).unwrap();
        let j_key = json_to_string(&self.timestamp.timestamp()).unwrap();

        writeln!(file_wrt, "{}: {}", j_key, j_value)
    }
}

#[derive(Debug)]
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

    pub fn get_nb_nodes(&self, ovh_nodes: OvhNodeFilter) -> i32 {
        match ovh_nodes {
            OvhNodeFilter::Ovh => self.get_internal_routers().len() as i32,
            OvhNodeFilter::External => self.get_peering_routers().len() as i32,
            OvhNodeFilter::All => self.data.len() as i32,
        }
    }

    pub fn get_nb_links(&self, ovh_nodes: OvhNodeFilter) -> i32 {
        (self
            .data
            .values()
            .filter(|router| match ovh_nodes {
                OvhNodeFilter::Ovh => !router.is_external(),
                OvhNodeFilter::External => router.is_external(),
                OvhNodeFilter::All => true,
            })
            .map(|router| {
                router
                    .peers
                    .iter()
                    .filter(|(peer_name, _)| match ovh_nodes {
                        OvhNodeFilter::Ovh => !is_peer_from_name(peer_name),
                        _ => true,
                    })
                    .map(|(_, peering)| peering.len())
                    .sum::<usize>()
            })
            .sum::<usize>()
            / match ovh_nodes {
                OvhNodeFilter::External => 1, //
                _ => 2,
            }) as i32
    }

    /// For each router in the network, computes the ECMP imbalance,
    /// i.e., the difference in load between all links with the same source and destination.
    /// We do *not* take into account the loads of:
    ///     - 0%: no traffic, unused link,
    ///     - 1%: assume that it represents only traffic control
    pub fn get_ecmp_imbalance(&self, ovh_nodes: OvhNodeFilter) -> Vec<i8> {
        // I first made it using functional programming, but it is way cleaner like this
        let mut output: Vec<i8> = Vec::with_capacity(self.data.len()); // Random initialization
        for router in self.data.values().filter(|&r| match ovh_nodes {
            OvhNodeFilter::Ovh => !r.is_external(),
            OvhNodeFilter::External => r.is_external(),
            OvhNodeFilter::All => true,
        }) {
            for (_, peer_links) in router
                .peers
                .iter()
                .filter(|(peer_name, _)| match ovh_nodes {
                    OvhNodeFilter::Ovh => &&peer_name.to_uppercase() != peer_name,
                    _ => true,
                })
            {
                let filtered_links: Vec<&Link> =
                    peer_links.iter().filter(|&link| link.load > 1).collect();
                if filtered_links.len() > 1 {
                    let min_load = filtered_links
                        .iter()
                        .fold(filtered_links[0].load, |a, b| cmp::min(a, b.load))
                        as i8;
                    let max_load = filtered_links
                        .iter()
                        .fold(filtered_links[0].load, |a, b| cmp::max(a, b.load))
                        as i8;
                    output.push(max_load - min_load);
                }
            }
        }

        output
    }

    pub fn get_nb_ecmp_links(&self, ovh_nodes: OvhNodeFilter) -> Vec<i8> {
        let mut output: Vec<i8> = Vec::with_capacity(self.data.len());
        for router in self.data.values().filter(|&r| match ovh_nodes {
            OvhNodeFilter::Ovh => !r.is_external(),
            OvhNodeFilter::External => r.is_external(),
            OvhNodeFilter::All => true,
        }) {
            for (_, peer_links) in router
                .peers
                .iter()
                .filter(|(peer_name, _)| match ovh_nodes {
                    OvhNodeFilter::Ovh => !is_peer_from_name(peer_name),
                    _ => true,
                })
            {
                if peer_links.len() > 1 {
                    output.push(peer_links.len() as i8);
                }
            }
        }

        output
    }

    pub fn get_link_loads(&self, ovh_nodes: OvhNodeFilter) -> Vec<i8> {
        let mut output: Vec<i8> = Vec::with_capacity(self.data.len());
        for router in self.data.values().filter(|&r| match ovh_nodes {
            OvhNodeFilter::Ovh => !r.is_external(),
            OvhNodeFilter::External => r.is_external(),
            OvhNodeFilter::All => true,
        }) {
            for (_, peer_links) in router
                .peers
                .iter()
                .filter(|(peer_name, _)| match ovh_nodes {
                    OvhNodeFilter::Ovh => is_peer_from_name(peer_name),
                    _ => true,
                })
            {
                peer_links
                    .iter()
                    .filter(|&link| link.load > 1)
                    .for_each(|link| output.push(link.load as i8));
            }
        }

        output
    }
}

/// TODO: this function needs to be refactored, because it uses
/// my *very few* skills in Rust
pub fn parse_yaml(filepath: &str, timestamp: NaiveDateTime) -> Option<OvhData> {
    let fd = std::fs::File::open(filepath).unwrap();
    let document: Value = match from_reader(fd) {
        Ok(doc) => doc,
        Err(err) => {
            println!("Error on {}: {:?}", filepath, err);
            return None;
        }
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
                            return None;
                        }
                    },
                    None => {
                        println!("Parsing problem (2) with the file: {}", filepath);
                        return None;
                    }
                };
                let peer = match link.get(&k_peer) {
                    //p.as_str().unwrap(),
                    Some(p) => match p.as_str() {
                        Some(n) => n,
                        None => {
                            println!("Parsing problem (3) with the file: {}, {:?}", filepath, p);
                            return None;
                        }
                    },
                    None => {
                        println!("Parsing problem (4) with the file {}", filepath);
                        return None;
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

pub fn aggregate_by_time(
    all_data: &[ExperimentResults],
) -> Vec<(NaiveDate, Vec<&ExperimentResults>)> {
    let mut aggr: Vec<(NaiveDate, Vec<&ExperimentResults>)> = Vec::with_capacity(10);
    let mut last_time_in = all_data[0].timestamp.date();
    let mut current_time: Vec<&ExperimentResults> = Vec::with_capacity(100);

    let mut i = 0;
    // for experiment in all_data
    while i < all_data.len() {
        let experiment = &all_data[i];
        if experiment.timestamp.date().month() == last_time_in.month()
            && experiment.timestamp.date().year() == last_time_in.year()
        {
            // Same month, aggregate
            current_time.push(experiment);
            i += 1; // Next data, in order, same month
        } else {
            // Changing the month... Add the vector in aggregated and clear the buffer
            let tmp = current_time;
            aggr.push((last_time_in, tmp));

            if (experiment.timestamp.date() - last_time_in).num_days() < 33 {
                current_time = vec![experiment]; // Add current data in a new clear buffer
                i += 1; // Next data, in order but next month
                last_time_in = experiment.timestamp.date();
            } else {
                // Oh... There is a gap in the data of more than 1 month... Need to fill the gap
                current_time = Vec::new();
                let mut current_year = last_time_in.year();
                let mut current_month = last_time_in.month();
                current_month = match current_month {
                    12 => {
                        current_year += 1;
                        1
                    }
                    _ => current_month + 1,
                };
                last_time_in = NaiveDate::from_ymd(current_year, current_month, 1); // Next month
                aggr.push((last_time_in, Vec::new()));
            }
        }
    }

    if !current_time.is_empty() {
        aggr.push((last_time_in, current_time));
    }

    aggr
}

pub fn aggregate_ecmp_diff<'a>(
    aggr: &[(NaiveDate, Vec<&'a ExperimentResults>)],
    ovh_nodes: OvhNodeFilter,
) -> Vec<Vec<&'a i8>> {
    aggr.iter()
        .map(|(_, one_aggr)| {
            one_aggr
                .iter()
                .flat_map(|&exp| match ovh_nodes {
                    OvhNodeFilter::Ovh => &exp.ecmp_diffs_ovh,
                    OvhNodeFilter::External => &exp.ecmp_diffs_external,
                    OvhNodeFilter::All => &exp.ecmp_diffs,
                })
                .collect::<Vec<&i8>>()
        })
        .collect()
}

pub fn write_csv_ecmp_aggregated(
    aggr: &[(NaiveDate, Vec<&ExperimentResults>)],
    wrt: &mut Writer<File>,
    wrt_total: &mut Writer<File>,
    ovh_nodes: OvhNodeFilter,
    ranges: &[i8],
) -> Result<(), csv::Error> {
    let aggr_ecmp = aggregate_ecmp_diff(aggr, ovh_nodes);

    for (exp_aggr, ecmp_values) in aggr.iter().zip(aggr_ecmp) {
        let cnts = ranges
            .windows(2)
            .map(|slice| {
                if !ecmp_values.is_empty() {
                    ecmp_values.iter().filter(|&&&v| slice.contains(&v)).count() as i32
                } else {
                    0
                }
            })
            .collect::<Vec<i32>>();
        let naivedatetime = NaiveDateTime::new(exp_aggr.0, NaiveTime::from_hms(0, 0, 0));
        wrt.serialize((naivedatetime.timestamp(), &cnts))?;
        wrt_total.serialize((naivedatetime.timestamp(), ecmp_values.len()))?;
    }

    Ok(())
}
