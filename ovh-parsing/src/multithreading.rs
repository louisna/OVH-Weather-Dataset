use indicatif::ProgressBar;
use ovh_parsing::{parse_yaml, ExperimentResults, FileMetadata};
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
                let nb_nodes = val.get_nb_nodes(None);
                let nb_nodes_ovh = val.get_nb_nodes(Some(true));
                let nb_nodes_external = val.get_nb_nodes(Some(false));
                let nb_links = val.get_nb_links(None);
                let nb_links_external = val.get_nb_links(Some(false));
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
