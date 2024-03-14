use actix_web::Responder;

pub async fn hello() -> impl Responder {
    "Hello World!"
}

pub async fn test() -> impl Responder {
    "test"
}
