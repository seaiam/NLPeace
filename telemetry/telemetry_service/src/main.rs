use actix_web::{App, HttpServer};
use notify::Watcher;
use notify::{Config, Event, EventHandler, PollWatcher, RecommendedWatcher, RecursiveMode, Result};
use std::process;
use std::sync::mpsc::channel;
use std::thread;
use std::time::Duration;

mod internal;

use internal::controller;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    watch().unwrap_or_else(|err| {
        eprintln!("Error watching config file: {}", err);
        // return
        process::exit(1);
    });

    println!("here");
    HttpServer::new(move || App::new().configure(controller::api::gen_router()))
        .bind("127.0.0.1:8080")?
        .run()
        .await
}

fn watch() -> Result<()> {
    let _handle = thread::spawn(|| -> Result<()> {
        let (tx, rx) = channel();
        let config = Config::default().with_poll_interval(std::time::Duration::from_secs(1));
        let mut watcher = RecommendedWatcher::new(tx, config)?;

        watcher.watch(
            std::path::Path::new("src/config_files/config.json"),
            RecursiveMode::NonRecursive,
        )?;

        println!("Started watching /path/to/watch");

        loop {
            match rx.recv() {
                Ok(event) => println!("Change detected: {:?}", event),
                Err(e) => println!("Watch error: {:?}", e),
            }
        }
    });
    Ok(())
}
