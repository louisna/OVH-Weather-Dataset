use ovh_parsing::{FileMetadata, parse_yaml};
use std::{fs, path::PathBuf};
use structopt::StructOpt;

#[derive(StructOpt)]
struct Cli {
    /// Directory containing the input yamls
    directory_path: String,
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

fn get_vec_values_from_idxs<'a, T>(vec: &'a [T], idxs: &[usize]) -> Vec<&'a T> {
    idxs.iter().map(|&i| &vec[i]).collect()
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
    println!(
        "Size total: {total}, size every two: {two}",
        total = files.len(),
        two = files_every_two_days.len()
    );

    // Test to see if we can have the router object
    let router = parse_yaml(&files[0].filepath);
    println!("Voici le routeur: {:?}", router[0]);
}
