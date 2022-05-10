use chrono::prelude::NaiveDateTime;
use std::{
    fs::{self},
    path::PathBuf,
};
use structopt::StructOpt;

#[derive(StructOpt)]
struct Cli {
    /// Directory containing the input yamls
    directory_path: String,
}

#[derive(Debug)]
struct FileMetadata {
    filepath: String,
    timestamp: NaiveDateTime,
}

impl FileMetadata {
    fn path_to_file_metadata(pathbuf: &PathBuf) -> Option<FileMetadata> {
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

/// Returns a Vec of indexes of the files one should take given the `step`
/// TODO: use an enum to be able to separate using days etc...
fn get_by_day_step(files: &[FileMetadata], step: i64) -> Vec<usize> {
    let mut output: Vec<usize> = Vec::with_capacity((files.len() as i64 / step + 1) as usize);
    
    // Init: take first file
    let mut last_in = &files[0];
    for (idx, f) in files.iter().enumerate() {
        if (f.timestamp - last_in.timestamp).num_days() >= step {
            output.push(idx);
            last_in = f;
        }
    }

    output
}

fn main() {
    let args = Cli::from_args();

    // https://stackoverflow.com/questions/58062887/filtering-files-or-directories-discovered-with-fsread-dir
    let paths: Vec<PathBuf> = fs::read_dir(&args.directory_path)
        .expect(&format!(
            "Impossible to open the directory: {dir}",
            dir = &args.directory_path
        ))
        .into_iter()
        .filter(|r| r.is_ok())
        .map(|r| r.unwrap().path())
        .collect();

    let mut files = paths
        .iter()
        .map(|pathbuf| FileMetadata::path_to_file_metadata(pathbuf))
        .filter(|option_meta| option_meta.is_some())
        .map(|optional| optional.unwrap())
        .collect::<Vec<FileMetadata>>();

    // Sort the files according to the timestamp
    files.sort_by(|a, b| a.timestamp.partial_cmp(&b.timestamp).unwrap());

    let files_every_two_days = get_by_day_step(&files, 2);
    println!("Size total: {total}, size every two: {two}", total=files.len(), two=files_every_two_days.len());
}
