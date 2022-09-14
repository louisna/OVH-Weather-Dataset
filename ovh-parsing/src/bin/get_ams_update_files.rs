use std::sync::mpsc::channel;
use clap::Parser;
use ovh_parsing::{OvhData, FileMetadata, parse_yaml, get_files::get_all_ovh_files, Link};
use threadpool::ThreadPool;
use std::collections::HashMap;
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
    let filtered_files = files.iter().filter_map(|f| if
        f.filepath.split("/").last().unwrap().split("_").last().unwrap().split(".").nth(0).unwrap().parse::<u64>().unwrap() >= 1646365511 &&
        f.filepath.split("/").last().unwrap().split("_").last().unwrap().split(".").nth(0).unwrap().parse::<u64>().unwrap() <= 1647575112
        {Some(f)} else {None} ).collect::<Vec<&FileMetadata>>();
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
    for r in output {
        println!("{:#?} {:#?}",
            r.timestamp,
            r.data
            .iter()
            .filter_map(|(_, r)|
                if r.is_external() && r.name == "AMS-IX" {Some((&r.name, r.peers.clone()))} // downstream
                else if r.has_external() {
                    //println!("{:#?}", r);
                    match r.peers.get("AMS-IX") {
                        Some(entry) => Some((&r.name, HashMap::from([("AMS-IX".to_string(), entry.clone())]))),
                        None => None
                    }
                }
                else {None}
            )
            .collect::<HashMap<&String, HashMap<String, Vec<Link>>>>()
            //[&"AMS-IX".to_string()]
        );
    }
}
fn main() {
    let args = Args::parse();
    let files = match get_all_ovh_files(&args.dir) {
        Ok(f) => f,
        Err(e) => panic!("Error when getting the files: {}", e),
    };
    get_results(&files, args.nb_threads);
}
