use actix_web::{guard, web, web::ServiceConfig};

use crate::controller::routes;


pub fn gen_router() -> Box<dyn FnOnce(&mut ServiceConfig)> {
    Box::new(move |config: &mut ServiceConfig| {
        config.service(
            web::scope("/submit")
                .service(
                    web::resource("/data")
                        .guard(guard::Any(guard::Get()).or(guard::Post()))
                        .route(web::get().to(routes::test)),
                )
                .service(web::resource("/data2").guard(guard::Get()).to(routes::hello)),
        );
    })
}
