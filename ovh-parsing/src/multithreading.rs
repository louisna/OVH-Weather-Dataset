use indicatif::ProgressBar;
use ovh_parsing::{parse_yaml, FileMetadata, OvhData};
use std::sync::mpsc::channel;
use threadpool::ThreadPool;

pub fn multithread_parsing(files: &[&FileMetadata], nb_threads: usize) -> Vec<OvhData> {
    let pool = ThreadPool::new(nb_threads);
    let (tx, rx) = channel();
    let pb = ProgressBar::new(files.len() as u64);

    for file in files {
        pb.inc(1);
        let tx = tx.clone();
        let s = file.filepath.to_owned();
        let timestamp = file.timestamp;
        pool.execute(move || {
            let data = parse_yaml(&s, timestamp);
            tx.send(data).expect("Could not send data");
        })
    }

    let mut output: Vec<OvhData> = Vec::with_capacity(files.len());
    for _ in 0..files.len() {
        let a = rx.recv().unwrap();
        output.push(a);
    }
    pb.finish_with_message("done");
    output.sort_by(|a, b| a.timestamp.cmp(&b.timestamp));
    output
}
