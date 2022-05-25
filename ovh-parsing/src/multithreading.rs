// Author: Louis Navarre <louis.navarre@uclouvain.be> (UCLouvain -- INL)
// Date: 11/05/2022

use indicatif::ProgressBar;
use ovh_parsing::{parse_yaml, ExperimentResults, FileMetadata, OvhNodeFilter};
use std::sync::mpsc::channel;
use std::time::Duration;
use threadpool::ThreadPool;

/// https://rust-lang-nursery.github.io/rust-cookbook/concurrency/threads.html
pub fn multithread_parsing(files: &[&FileMetadata], nb_threads: usize) -> Vec<ExperimentResults> {
    let pool = ThreadPool::new(nb_threads);
    let (tx, rx) = channel();
    let pb = ProgressBar::new(files.len() as u64);

    for file in files {
        let tx = tx.clone();
        let s = file.filepath.to_owned();
        let timestamp = file.timestamp;
        pool.execute(move || {
            if let Some(val) = parse_yaml(&s, timestamp) {
                let nb_nodes = val.get_nb_nodes(OvhNodeFilter::All);
                let nb_nodes_ovh = val.get_nb_nodes(OvhNodeFilter::Ovh);
                let nb_nodes_external = val.get_nb_nodes(OvhNodeFilter::External);
                let nb_links = val.get_nb_links(OvhNodeFilter::All);
                let nb_links_external = val.get_nb_links(OvhNodeFilter::External);
                let ecmp_diffs = val.get_ecmp_imbalance(OvhNodeFilter::All);
                let ecmp_diffs_ovh = val.get_ecmp_imbalance(OvhNodeFilter::Ovh);
                let ecmp_diffs_external = val.get_ecmp_imbalance(OvhNodeFilter::External);
                let loads = val.get_link_loads(OvhNodeFilter::All);
                let loads_ovh = val.get_link_loads(OvhNodeFilter::Ovh);
                let loads_external = val.get_link_loads(OvhNodeFilter::External);
                let nb_ecmp_links = val.get_nb_ecmp_links(OvhNodeFilter::All);
                let nb_ecmp_links_ovh = val.get_nb_ecmp_links(OvhNodeFilter::Ovh);
                let nb_ecmp_links_external = val.get_nb_ecmp_links(OvhNodeFilter::External);
                // Easier, because we should divide by two for internal links, but by 1
                // for peering links.
                let nb_links_ovh = nb_links - nb_links_external;
                tx.send(ExperimentResults {
                    timestamp,
                    nb_nodes,
                    nb_nodes_ovh,
                    nb_nodes_external,
                    nb_links,
                    nb_links_ovh,
                    nb_links_external,
                    ecmp_diffs,
                    ecmp_diffs_ovh,
                    ecmp_diffs_external,
                    loads,
                    loads_ovh,
                    loads_external,
                    nb_ecmp_links,
                    nb_ecmp_links_ovh,
                    nb_ecmp_links_external,
                    // ..Default::default()  // Just in case we add other fields, the code compiles
                })
                .expect("Could not send data");
            }
        })
    }

    let mut output: Vec<ExperimentResults> = Vec::with_capacity(files.len());
    let timeout = Duration::new(10, 0);
    for _ in 0..files.len() {
        if let Ok(result) = rx.recv_timeout(timeout) {
            output.push(result);
        }
    }
    pb.finish_with_message("done");
    output.sort_by(|a, b| a.timestamp.cmp(&b.timestamp));
    output
}
