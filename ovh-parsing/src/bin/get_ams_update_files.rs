use std::sync::mpsc::channel;

use clap::Parser;
use ovh_parsing::{get_files::get_all_ovh_files, parse_yaml, FileMetadata, Link, OvhData};
use std::collections::HashMap;
use threadpool::ThreadPool;

#[derive(Parser, Debug)]
#[clap(author, version, about, long_about = None)]
struct Args {
    /// Path to the directory containing the data
    #[clap(short, long, value_parser)]
    dir: String,
    /// Number of threads to parse the YAML files
    #[clap(short, long, value_parser, default_value_t = 4)]
    nb_threads: usize,
}

fn get_results(files: &[FileMetadata], nb_threads: usize) {
    let pool = ThreadPool::new(nb_threads);
    let (tx, rx) = channel();

    let filtered_files = files; // TODO

    filtered_files.iter().for_each(|file| {
        let tx = tx.clone();
        let s = file.filepath.to_owned();
        let timestamp = file.timestamp;
        pool.execute(move || {
            let data_opt = parse_yaml(&s, timestamp);
            if let Some(data) = data_opt {
                tx.send(Some(data)).unwrap();
            } else {
                tx.send(None).unwrap();
            }
        })
    });

    let mut output: Vec<OvhData> = Vec::with_capacity(filtered_files.len());

    for _ in 0..files.len() {
        match rx.recv() {
            Err(e) => println!("Error: {:?}", e),
            Ok(None) => println!("None received"),
            Ok(Some(v)) => output.push(v),
        }
    }

    output.sort_by(|a, b| a.timestamp.partial_cmp(&b.timestamp).unwrap());

    // TODO
}

fn main() {
    let args = Args::parse();

    let files = match get_all_ovh_files(&args.dir) {
        Ok(f) => f,
        Err(e) => panic!("Error when getting the files: {}", e),
    };

    get_results(&files, args.nb_threads);
}
