use ovh_parsing::{Router, Link};
use csv::WriterBuilder;
use std::error::Error;
use serde::Serialize;

fn write_in_csv<T: Serialize>(values: T, filepath: &str) -> Result<(), Box<dyn Error>> {
    let mut wrt = WriterBuilder::new()
        .has_headers(false)
        .from_path(filepath)?;
    
    wrt.serialize(values)?;

    Ok(())
}

pub fn nb_router_evolution(values: &[Vec<Router>], output_csv: &str) -> Result<(), Box<dyn Error>> {
    let res = values.iter().map(
        |one_timestamp| one_timestamp.len() 
    ).collect::<Vec<usize>>();
    
    write_in_csv(res, output_csv)
}