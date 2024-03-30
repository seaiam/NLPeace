use actix_web::{guard, web, web::ServiceConfig};
use serde::Serialize;
use sqlx::{self, FromRow};
use crate::controller::routes;

#[derive(Serialize, FromRow)]
struct User {
    id: i32,
    first_name: String,
    last_name: String,
}

pub fn gen_router() -> Box<dyn FnOnce(&mut ServiceConfig)> {
    Box::new(move |config: &mut ServiceConfig| {
        config.service(
            web::scope("/submit")
                .service(
                    web::resource("/requests").route(web::get().to(routes::get_requests)),
                )
                .service(
                    web::resource("/data2")
                        .guard(guard::Post())
                        .to(routes::post_request),
                )
                .service(
                    web::resource("/data3")
                        .guard(guard::Post())
                        .to(routes::post_response),
                )
                .service(
                    web::resource("/data4")
                        .guard(guard::Get())
                        .to(routes::get_stats),
                )
                .service(
                    web::resource("/healthcheck")
                        .guard(guard::Get())
                        .to(routes::get_is_healthy),
                )
                .service(
                    web::resource("/popular")
                        .guard(guard::Get())
                        .to(routes::get_popular_traffic),
                ).service(
                    web::resource("/restart")
                        .guard(guard::Get())
                        .to(routes::restart_service),
                ).service(
                    web::resource("/response")
                        .guard(guard::Get())
                        .to(routes::get_response),
                ),
        );
    })
}

