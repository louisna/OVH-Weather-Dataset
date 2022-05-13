use chrono::Duration;
use csv::{Writer, WriterBuilder};
// use indicatif::ProgressBar;
use ovh_parsing::{ExperimentResults, FileMetadata};
use std::error::Error;
use std::fs::File;
use std::io::Write;
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
    /// Presice starting time of the selection, in the same unit at the `unit_step`
    // #[structopt(short = "p")]
    // precise_start_time: Option<String>,
    #[structopt(short = "o", default_value = "csv")]
    output_dir: String,
    /// Number of threads used to parse the yaml files
    #[structopt(short = "n", default_value = "4")]
    nb_threads: u32,
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

// TODO
/*fn get_by_unit_step_precise_time<F>(files: &[FileMetadata], step: i64, step_function: F, start_time: NaiveDateTime) -> Vec<usize>
where
    F: Fn(Duration) -> i64,
{
    let mut output: Vec<usize> = Vec::with_capacity((files.len() as i64 / step + 1) as usize);

    // Find the first file that follows the `start_time` constrain
    // TODO
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
*/

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

    let idxs_selected = match args.unit_step.as_ref() {
        "all" => get_by_files_step(&files, args.step),
        _ => get_by_unit_step(&files, args.step, step_function),
    };
    println!(
        "Size total: {total}, size after selection: {two}",
        total = files.len(),
        two = idxs_selected.len()
    );

    let files_selected = get_vec_values_from_idxs(&files, &idxs_selected);

    // let pb = ProgressBar::new(files_selected.len() as u64);
    // let all_routers_sel_tmsp = files_selected
    //     .iter()
    //     .map(|&x| {
    //         pb.inc(1);
    //         parse_yaml(&x.filepath, x.timestamp)
    //     })
    //     .collect::<Vec<OvhData>>();
    // pb.finish_with_message("done");

    let all_results = multithread_parsing(&files_selected, args.nb_threads as usize);

    let all_writers = [
        |x: &ExperimentResults, wrt: &mut Writer<File>| x.write_csv_nb_nodes(wrt, None),
        |x: &ExperimentResults, wrt: &mut Writer<File>| x.write_csv_nb_nodes(wrt, Some(true)),
        |x: &ExperimentResults, wrt: &mut Writer<File>| x.write_csv_nb_nodes(wrt, Some(false)),
        |x: &ExperimentResults, wrt: &mut Writer<File>| x.write_csv_nb_nodes(wrt, None),
        |x: &ExperimentResults, wrt: &mut Writer<File>| x.write_csv_nb_nodes(wrt, Some(true)),
        |x: &ExperimentResults, wrt: &mut Writer<File>| x.write_csv_nb_nodes(wrt, Some(false)),
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

    // Json parsing is a bit different
    let all_filenames_json = ["ecmp-diffs.yaml"];

    for filename in all_filenames_json {
        // Clean file
        let mut file_wrt = std::fs::File::create(Path::new(&args.output_dir).join(filename))?;
        write!(&mut file_wrt, "---").unwrap();
        all_results
            .iter()
            .for_each(|res| res.write_yaml_ecmp_diff(&mut file_wrt).unwrap())
    }

    Ok(())
}
