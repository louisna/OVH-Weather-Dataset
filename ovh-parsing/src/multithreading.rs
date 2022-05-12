use indicatif::ProgressBar;
use ovh_parsing::{parse_yaml, FileMetadata, ExperimentResults};
use std::sync::mpsc::channel;
use threadpool::ThreadPool;

/// https://rust-lang-nursery.github.io/rust-cookbook/concurrency/threads.html
pub fn multithread_parsing(files: &[&FileMetadata], nb_threads: usize, output_files: Vec<&str>) -> Vec<ExperimentResults> {
    let pool = ThreadPool::new(nb_threads);
    let (tx, rx) = channel();
    let pb = ProgressBar::new(files.len() as u64);

    for file in files {
        let tx = tx.clone();
        let s = file.filepath.to_owned();
        let timestamp = file.timestamp;
        pool.execute(move || {
            if let Some(val) = parse_yaml(&s, timestamp) {
                let nb_nodes = val.get_nb_nodes();
                let nb_links = val.get_nb_links();
                tx.send(ExperimentResults {nb_nodes, nb_links, timestamp}).expect("Could not send data");
            }
        })
    }

    let mut output: Vec<ExperimentResults> = Vec::with_capacity(files.len());
    for _ in 0..files.len() {
        let result = rx.recv().unwrap();
        output.push(result);
    }
    pb.finish_with_message("done");
    output.sort_by(|a, b| a.timestamp.cmp(&b.timestamp));
    output
}
