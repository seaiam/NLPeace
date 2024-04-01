use actix_web::{web::Data, App, HttpServer};
use dotenv::dotenv;
use sqlx::{postgres::PgPoolOptions, Pool, Postgres};

mod internal;
use internal::controller;

pub struct AppState {
    db: Pool<Postgres>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    app_start()
        .await
        .unwrap_or_else(|e| eprintln!("error occures starting the app: {:?}", e));
    Ok(())
}

async fn app_start() -> std::io::Result<()> {
    let path = dotenv().ok();
    println!("{:?}", path);
    let database_url =
        std::env::var("DATABASE_URL").unwrap_or_else(|e| format!("db must be initialized {:?}", e));
    println!("db string {}", database_url);

    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&database_url)
        .await
        .expect("error building a connection pool");

    println!("Starting Service...");
    HttpServer::new(move || {
        App::new()
            .app_data(Data::new(AppState { db: pool.clone() }))
            .configure(controller::api::gen_router())
    })
    .bind("0.0.0.0:8080")?
    .run()
    .await
}
