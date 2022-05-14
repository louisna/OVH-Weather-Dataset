use chrono::Duration;
use csv::{Writer, WriterBuilder};
// use indicatif::ProgressBar;
use ovh_parsing::{aggregate_by_time, write_csv_ecmp_aggregated, ExperimentResults, FileMetadata};
use std::error::Error;
use std::fs::File;
use std::path::Path;
use std::{fs, path::PathBuf};
use structopt::StructOpt;

use crate::multithreading::multithread_parsing;
mod basic_analyzis;
mod multithreading;

const UNIT_STEP: &[&str] = &["all", "hour", "day"];

#[derive(StructOpt)]
struct Cli {
    /// Directory containing the input yamls
    directory_path: String,
    /// The unit of time we use for the steps. Default "all" considers all files
    #[structopt(short = "u", possible_values(UNIT_STEP), default_value = "all")]
    unit_step: String,
    /// Step value to skip files with unit `unit_step`
    #[structopt(short = "s", default_value = "1")]
    step: i64,
    /// Output directory where all the CSV results files will be stored
    #[structopt(short = "o", default_value = ".")]
    output_dir: String,
    /// Number of threads used to parse the yaml files
    #[structopt(short = "n", default_value = "4")]
    nb_threads: u32,
    /// Start the parsing at the very specified timestamp
    #[structopt(long = "start-timestamp")]
    start_specific_timestamp: Option<i64>,
    /// Stop the parsing at the very specified timestamp
    #[structopt(long = "stop-timestamp")]
    stop_timestamp: Option<i64>,
}

/// Returns a Vec of indexes of the files one should take given the `step`
/// TODO: use an enum to be able to separate using days etc...
fn get_by_unit_step<F>(files: &[FileMetadata], step: i64, step_function: F) -> Vec<usize>
where
    F: Fn(Duration) -> i64,
{
    let mut output: Vec<usize> = Vec::with_capacity((files.len() as i64 / step + 1) as usize);

    // Init: take first file
    let mut last_in = &files[0];
    output.push(0);
    for (idx, f) in files.iter().enumerate() {
        if step_function(f.timestamp - last_in.timestamp) >= step {
            output.push(idx);
            last_in = f;
        }
    }

    output
}

fn cut_start_stop_timestamp(
    files: &[FileMetadata],
    start_timestamp: i64,
    stop_timestamp: Option<i64>,
) -> &[FileMetadata] {
    // 1. Find the file with the timestamp `start_timestamp`
    // TODO: find the closest if cannot find the precise one?
    // TODO: could benefit from binary search because the array slice is sorted
    let start_idx = match files
        .iter()
        .position(|file| file.timestamp.timestamp() == start_timestamp)
    {
        Some(idx) => idx,
        None => panic!("Could not find the desired timestamp: {}", start_timestamp),
    };

    // Breaking condition: stop including files after this timestamp
    // If option was None => include until the end
    let final_timestamp = match stop_timestamp {
        Some(t) => t,
        None => files[files.len() - 1].timestamp.timestamp(),
    };

    if start_timestamp >= final_timestamp {
        panic!(
            "The start timestamp should be lower than the stop timestamp: {} >= {}",
            start_timestamp, final_timestamp
        );
    }

    let stop_idx = match files // Could skip the first few timestamps because higher than start
        .iter()
        .position(|file| file.timestamp.timestamp() == final_timestamp)
    {
        Some(idx) => idx,
        None => panic!(
            "Could not find the final desired timestamp: {}",
            final_timestamp
        ),
    };

    &files[start_idx..stop_idx + 1]
}

fn get_by_files_step(files: &[FileMetadata], step: i64) -> Vec<usize> {
    (0..files.len()).step_by(step as usize).collect()
}

fn get_vec_values_from_idxs<'a, T>(vec: &'a [T], idxs: &[usize]) -> Vec<&'a T> {
    idxs.iter().map(|&i| &vec[i]).collect()
}

fn main() -> Result<(), Box<dyn Error>> {
    let args = Cli::from_args();

    // https://stackoverflow.com/questions/58062887/filtering-files-or-directories-discovered-with-fsread-dir
    let paths: Vec<PathBuf> = fs::read_dir(&args.directory_path)
        .unwrap_or_else(|_| {
            panic!(
                "Impossible to open the directory: {dir}",
                dir = &args.directory_path
            )
        })
        .into_iter()
        .filter(|r| r.is_ok())
        .map(|r| r.unwrap().path())
        .collect();

    let mut files = paths
        .iter()
        .map(|pathbuf| FileMetadata::path_to_file_metadata(pathbuf))
        .flatten()
        .collect::<Vec<FileMetadata>>();

    // Sort the files according to the timestamp
    files.sort_by(|a, b| a.timestamp.partial_cmp(&b.timestamp).unwrap());

    let step_function = match args.unit_step.as_ref() {
        "hour" => |x: Duration| x.num_hours(),
        "day" => |x: Duration| x.num_days(),
        "all" => |_| 0,
        _ => panic!("Unknown unit step!"),
    };

    let sliced_time_window = match args.start_specific_timestamp {
        Some(start_timestamp) => {
            cut_start_stop_timestamp(&files, start_timestamp, args.stop_timestamp)
        }
        None => &files,
    };

    let idxs_selected = match args.unit_step.as_ref() {
        "all" => get_by_files_step(sliced_time_window, args.step),
        _ => get_by_unit_step(sliced_time_window, args.step, step_function),
    };
    println!(
        "Size total: {total}, size after selection: {two}",
        total = files.len(),
        two = idxs_selected.len()
    );

    let files_selected = get_vec_values_from_idxs(sliced_time_window, &idxs_selected);

    let all_results = multithread_parsing(&files_selected, args.nb_threads as usize);
    let all_writers = [
        |x: &ExperimentResults, wrt: &mut Writer<File>| x.write_csv_nb_nodes(wrt, None),
        |x: &ExperimentResults, wrt: &mut Writer<File>| x.write_csv_nb_nodes(wrt, Some(true)),
        |x: &ExperimentResults, wrt: &mut Writer<File>| x.write_csv_nb_nodes(wrt, Some(false)),
        |x: &ExperimentResults, wrt: &mut Writer<File>| x.write_csv_nb_links(wrt, None),
        |x: &ExperimentResults, wrt: &mut Writer<File>| x.write_csv_nb_links(wrt, Some(true)),
        |x: &ExperimentResults, wrt: &mut Writer<File>| x.write_csv_nb_links(wrt, Some(false)),
    ];

    let all_filenames = [
        "nb-nodes-all.csv",
        "nb-nodes-ovh.csv",
        "nb-nodes-external.csv",
        "nb-links-all.csv",
        "nb-links-ovh.csv",
        "nb-links-external.csv",
    ];

    for (wrt_fn, filename) in all_writers.iter().zip(all_filenames) {
        let mut wrt = WriterBuilder::new()
            .has_headers(false)
            .from_path(Path::new(&args.output_dir).join(filename))?;
        all_results
            .iter()
            .for_each(|res| wrt_fn(res, &mut wrt).unwrap())
    }

    let all_writers_yaml = [
        |x: &ExperimentResults, wrt: &mut File| x.write_yaml_ecmp_diff(wrt, None),
        |x: &ExperimentResults, wrt: &mut File| x.write_yaml_ecmp_diff(wrt, Some(true)),
        |x: &ExperimentResults, wrt: &mut File| x.write_yaml_ecmp_diff(wrt, Some(false)),
    ];

    // YAML parsing is a bit different
    let all_filenames_yaml = [
        "ecmp-diffs-all.yaml",
        "ecmp-diffs-ovh.yaml",
        "ecmp-diffs-external.yaml",
    ];

    for (wrt_fn, filename) in all_writers_yaml.iter().zip(all_filenames_yaml) {
        // Clean file
        let mut file_wrt = std::fs::File::create(Path::new(&args.output_dir).join(filename))?;
        all_results
            .iter()
            .for_each(|res| wrt_fn(res, &mut file_wrt).unwrap())
    }

    // ECMP aggregation
    let aggregated = aggregate_by_time(&all_results);
    let ranges: &[i8; 9] = &[0, 1, 2, 3, 4, 5, 6, 7, 100];
    let ranges_str: Vec<String> = ranges
        .windows(2)
        .map(|slice| format!("[{},{}[", slice[0], slice[1]))
        .collect();
    let mut wrt_values = WriterBuilder::new()
        .has_headers(true)
        .delimiter(b';')
        .from_path(Path::new(&args.output_dir).join("ecmp-agg-values-all.csv"))?;
    let mut wrt_total = WriterBuilder::new()
        .has_headers(true)
        .delimiter(b';')
        .from_path(Path::new(&args.output_dir).join("ecmp-agg-total-all.csv"))?;
    // Write the headers
    wrt_values.serialize(("Time", ranges_str))?;
    wrt_total.serialize(("Time", "Total"))?;
    write_csv_ecmp_aggregated(&aggregated, &mut wrt_values, &mut wrt_total, None, ranges)?;

    Ok(())
}
