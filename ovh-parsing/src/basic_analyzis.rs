use ovh_parsing::{write_in_csv, FileMetadata, OvhData};
use std::error::Error;
use std::iter::Iterator;

pub fn _nb_router_evolution(
    values: &[OvhData],
    files: &[&FileMetadata],
    output_csv: &str,
) -> Result<(), Box<dyn Error>> {
    let res = values
        .iter()
        .map(|one_timestamp| one_timestamp.data.len())
        .collect::<Vec<usize>>();

    let serialized = res
        .iter()
        .zip(files)
        .map(|(&value, &file)| (file.timestamp.timestamp(), value))
        .collect::<Vec<(i64, usize)>>();

    write_in_csv(serialized, output_csv)
}

fn _compute_nb_links(one_timestamp: &OvhData) -> usize {
    one_timestamp
        .data
        .values()
        .map(|router| {
            router
                .peers
                .values()
                .map(|peering| peering.len())
                .sum::<usize>()
        })
        .sum::<usize>()
        / 2
}

pub fn _nb_links_evolution(
    values: &[OvhData],
    files: &[&FileMetadata],
    output_csv: &str,
) -> Result<(), Box<dyn Error>> {
    let res = values.iter().map(_compute_nb_links).collect::<Vec<usize>>();

    let serialized = res
        .iter()
        .zip(files)
        .map(|(&value, &file)| (file.timestamp.timestamp(), value))
        .collect::<Vec<(i64, usize)>>();

    write_in_csv(serialized, output_csv)
}

pub fn _node_degree_evolution(
    values: &[OvhData],
    files: &[&FileMetadata],
    _output_csv: &str,
) -> Result<(), Box<dyn Error>> {
    let res = values
        .iter()
        .map(|one_timestamp| {
            one_timestamp
                .data
                .iter()
                .map(|(_, router)| router.peers.len())
                .collect::<Vec<usize>>()
        })
        .collect::<Vec<Vec<usize>>>();

    let _serialized = res
        .iter()
        .zip(files)
        .map(|(v, &file)| (file.timestamp.timestamp(), v))
        .collect::<Vec<(i64, &Vec<usize>)>>();

    // TODO: for now impossible to parse in CSV because the number of columns vary
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::NaiveDateTime;
    use ovh_parsing::{Link, Router};
    use std::collections::HashMap;

    #[test]
    fn test_compute_nb_links() {
        let square = construct_square_graph();
        assert_eq!(_compute_nb_links(&square), 6);
    }

    fn construct_square_graph() -> OvhData {
        let mut square: HashMap<String, Router> = HashMap::new();

        let mut peers: HashMap<String, Vec<Link>> = HashMap::new();
        peers.insert(
            "b".to_string(),
            vec![Link {
                label: "1".to_string(),
                load: 30,
            }],
        );
        peers.insert(
            "c".to_string(),
            vec![
                Link {
                    label: "1".to_string(),
                    load: 25,
                },
                Link {
                    label: "1".to_string(),
                    load: 26,
                },
            ],
        );
        square.insert(
            "a".to_string(),
            Router {
                name: "a".to_string(),
                peers,
            },
        );

        let mut peers: HashMap<String, Vec<Link>> = HashMap::new();
        peers.insert(
            "a".to_string(),
            vec![Link {
                label: "1".to_string(),
                load: 10,
            }],
        );
        peers.insert(
            "d".to_string(),
            vec![Link {
                label: "1".to_string(),
                load: 1,
            }],
        );
        square.insert(
            "b".to_string(),
            Router {
                name: "b".to_string(),
                peers,
            },
        );

        let mut peers: HashMap<String, Vec<Link>> = HashMap::new();
        peers.insert(
            "a".to_string(),
            vec![
                Link {
                    label: "1".to_string(),
                    load: 50,
                },
                Link {
                    label: "1".to_string(),
                    load: 51,
                },
            ],
        );
        peers.insert(
            "d".to_string(),
            vec![
                Link {
                    label: "1".to_string(),
                    load: 75,
                },
                Link {
                    label: "2".to_string(),
                    load: 72,
                },
            ],
        );
        square.insert(
            "c".to_string(),
            Router {
                name: "c".to_string(),
                peers,
            },
        );

        let mut peers: HashMap<String, Vec<Link>> = HashMap::new();
        peers.insert(
            "b".to_string(),
            vec![Link {
                label: "1".to_string(),
                load: 50,
            }],
        );
        peers.insert(
            "c".to_string(),
            vec![
                Link {
                    label: "1".to_string(),
                    load: 2,
                },
                Link {
                    label: "2".to_string(),
                    load: 3,
                },
            ],
        );
        square.insert(
            "d".to_string(),
            Router {
                name: "d".to_string(),
                peers,
            },
        );

        OvhData {
            data: square,
            timestamp: NaiveDateTime::from_timestamp(1, 0),
        }
    }
}
