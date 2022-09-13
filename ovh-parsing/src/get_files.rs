use crate::FileMetadata;
use std::fs;
use std::path::PathBuf;

pub fn get_all_ovh_files(dirpath: &str) -> Result<Vec<FileMetadata>, String> {
    let paths: Vec<PathBuf> = match fs::read_dir(dirpath) {
        Ok(o) => o,
        Err(e) => return Err(format!("Could not open directory: {:?}", e)),
    }
    .into_iter()
    .filter(|r| r.is_ok())
    .map(|r| r.unwrap().path())
    .collect();

    let mut files = paths
        .iter()
        .map(|pathbuf| FileMetadata::path_to_file_metadata(pathbuf))
        .flatten()
        .collect::<Vec<FileMetadata>>();

    files.sort_by(|a, b| a.timestamp.partial_cmp(&b.timestamp).unwrap());

    Ok(files)
}
