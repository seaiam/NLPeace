use actix_web::{guard, web, web::ServiceConfig};
use serde::Serialize;
use sqlx::{self, FromRow};
use crate::controller::routes;


pub fn gen_router() -> Box<dyn FnOnce(&mut ServiceConfig)> {
    Box::new(move |config: &mut ServiceConfig| {
        config.service(
            web::scope("/submit")
                .service(
                    web::resource("/requests").route(web::get().to(routes::get_requests)), //         .guard(guard::Any(guard::Get()).or(guard::Post()))
                                                                                       //         .route(web::get().to(insert_request)),
                )
                .service(
                    web::resource("/data2")
                        // .guard(guard::Header("content-type", "text/json"))
                        .guard(guard::Post())
                        .to(routes::post_request),
                )
                .service(
                    web::resource("/data3")
                        // .guard(guard::Header("content-type", "text/json"))
                        .guard(guard::Post())
                        .to(routes::post_response),
                )
                .service(
                    web::resource("/data4")
                        // .guard(guard::Header("content-type", "text/json"))
                        .guard(guard::Get())
                        .to(routes::get_stats),
                )
                .service(
                    web::resource("/healthcheck")
                        // .guard(guard::Header("content-type", "text/json"))
                        .guard(guard::Get())
                        .to(routes::get_is_healthy),
                )
                .service(
                    web::resource("/popular")
                        // .guard(guard::Header("content-type", "text/json"))
                        .guard(guard::Get())
                        .to(routes::get_popular_traffic),
                ).service(
                    web::resource("/restart")
                        // .guard(guard::Header("content-type", "text/json"))
                        .guard(guard::Get())
                        .to(routes::restart_service),
                ),
        );
    })
}

