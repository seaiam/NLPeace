use serde_derive::Deserialize;
use serde_json;
use std::fs;

#[derive(Deserialize, Debug)]
pub struct Config {
    pub urls: [String; 2],
    pub polling_rate: i16,
}
const PATH_TO_CONFIG: &str = "./src/config.json";

pub fn import_config() -> Result<Config, Box<dyn std::error::Error>> {
    let data = fs::read_to_string(PATH_TO_CONFIG)?;

    // Parse the string into your data structure
    let parsed_data: Config = serde_json::from_str(&data)?;

    // You can now use `parsed_data` as a regular Rust struct
    println!("{:?}", parsed_data);

    Ok(parsed_data)
}
