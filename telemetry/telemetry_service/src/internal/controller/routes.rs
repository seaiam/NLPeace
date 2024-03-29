use crate::AppState;
use ::chrono::Utc;
use actix_web::web::{Data, Json};
use actix_web::{HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use sqlx::types::chrono::DateTime;
use sqlx::types::Uuid;
use sqlx::{self, FromRow};
use std::process::Command;

#[derive(Deserialize, Serialize, FromRow, Debug)]
pub struct Request {
    user_id: i32,
    request_body: String,
    url: String,
}

#[derive(Deserialize, Serialize, FromRow, Debug)]
pub struct Response {
    user_id: i32,
    status_code: i32,
}

#[derive(Deserialize, Serialize, FromRow, Debug)]
pub struct ResponseDB {
    response_id: Uuid,
    user_id: i32,
    status_code: i32,
    response_time: DateTime<Utc>,
}
#[derive(Deserialize, Serialize, FromRow, Debug)]

pub struct RequestDB {
    request_id: Uuid,
    user_id: i32,
    request_body: String,
    url: String,
    request_time: DateTime<Utc>,
}

pub async fn post_request(state: Data<AppState>, body: Json<Request>) -> impl Responder {
    println!("post_request");
    match sqlx::query(
        "INSERT INTO request (request_id, user_id, request_body, request_time, url) 
        Values (gen_random_uuid(), $1, $2, NOW(), $3)",
    )
    .bind(body.user_id)
    .bind(&body.request_body.to_string())
    .bind(&body.url)
    .execute(&state.db)
    .await
    {
        Ok(_request) => HttpResponse::Ok(),
        Err(e) => {
            eprintln!("error occured inserting into db{}", e);
            HttpResponse::Conflict()
        }
    }
}

pub async fn post_response(state: Data<AppState>, body: Json<Response>) -> impl Responder {
    println!("post_response");
    match sqlx::query(
        "INSERT INTO response (response_id, user_id, status_code, response_time) 
        Values (gen_random_uuid(), $1, $2, NOW())",
    )
    .bind(body.user_id)
    .bind(body.status_code)
    .execute(&state.db)
    .await
    {
        Ok(_request) => HttpResponse::Ok(),
        Err(e) => {
            eprintln!("error occured inserting request into db{}", e);
            HttpResponse::Conflict()
        }
    }
}

pub async fn get_requests(state: Data<AppState>) -> impl Responder {
    match sqlx::query_as::<_, RequestDB>("SELECT * FROM request")
        .fetch_all(&state.db)
        .await
    {
        Ok(requests) => {
            requests
                .iter()
                .for_each(|request| println!("{:?}", request));
            HttpResponse::Ok().json(requests)
        }
        Err(e) => {
            eprintln!("error reading from db{}", e);
            HttpResponse::NotFound().json("No users found")
        }
    }
}

pub async fn get_response(state: Data<AppState>) -> impl Responder {
    match sqlx::query_as::<_, ResponseDB>("SELECT * FROM response")
        .fetch_all(&state.db)
        .await
    {
        Ok(requests) => {
            requests
                .iter()
                .for_each(|request| println!("{:?}", request));
            HttpResponse::Ok().json(requests)
        }
        Err(e) => {
            eprintln!("error reading from db{}", e);
            HttpResponse::NotFound().json("No users found")
        }
    }
}

#[derive(Deserialize, Serialize, Debug)]

struct Stats {
    not_found_stats: NotFoundStats,
    bad_request_stats: BadRequestStats,
    intern_server_error_stats: InternalServerErrorStats,
    ok_stats: OkStats,
    not_found: Vec<ResponseDB>,
    bad_request: Vec<ResponseDB>,
    internal_server_error: Vec<ResponseDB>,
    ok: Vec<ResponseDB>,
}

#[derive(Deserialize, Serialize, Debug, Default)]

struct NotFoundStats {
    percent: String,
    total_number: u16,
}
#[derive(Deserialize, Serialize, Debug)]

struct BadRequestStats {
    percent: String,
    total_number: u16,
}
#[derive(Deserialize, Serialize, Debug)]

struct InternalServerErrorStats {
    percent: String,
    total_number: u16,
}
#[derive(Deserialize, Serialize, Debug)]

struct OkStats {
    percent: String,
    total_number: u16,
}

pub async fn get_stats(state: Data<AppState>) -> impl Responder {
    let responses = sqlx::query_as::<sqlx::Postgres, ResponseDB>(
        "SELECT response_id, user_id, status_code, response_time FROM response",
    )
    .fetch_all(&state.db)
    .await
    .unwrap_or_else(|e| {
        eprintln!("error occured in db {}", e);
        Vec::new()
    });

    let mut not_found_list: Vec<ResponseDB> = Vec::new();
    let mut bad_request_list: Vec<ResponseDB> = Vec::new();
    let mut internal_server_error_list: Vec<ResponseDB> = Vec::new();
    let mut ok_list: Vec<ResponseDB> = Vec::new();

    responses
        .into_iter()
        .for_each(|response| match response.status_code {
            200 => ok_list.push(response),
            404 => not_found_list.push(response),
            500 => internal_server_error_list.push(response),
            400 => bad_request_list.push(response),
            _ => (),
        });

    let total_length = not_found_list.len()
        + bad_request_list.len()
        + internal_server_error_list.len()
        + ok_list.len();

    let stats: Stats = Stats {
        not_found_stats: NotFoundStats {
            percent: format!("{}%", (not_found_list.len() as f32 / total_length as f32)  * 100_f32),
            total_number: not_found_list.len() as u16,
        },
        bad_request_stats: BadRequestStats {
            percent: format!("{}%", (bad_request_list.len()as f32 / total_length as f32) * 100_f32),
            total_number: bad_request_list.len() as u16,
        },
        intern_server_error_stats: InternalServerErrorStats {
            percent: format!(
                "{}%",
                (internal_server_error_list.len() as f32 / total_length as f32) * 100_f32
            ),
            total_number: internal_server_error_list.len() as u16,
        },
        ok_stats: OkStats {
            percent: format!("{}%", (ok_list.len() as f32 / total_length as f32) * 100_f32),
            total_number: ok_list.len() as u16,
        },
        not_found: not_found_list,
        bad_request: bad_request_list,
        internal_server_error: internal_server_error_list,
        ok: ok_list,
    };
    HttpResponse::Ok().json(stats)
}

pub async fn get_is_healthy(state: Data<AppState>) -> impl Responder {
    let responses: Vec<Response> = sqlx::query_as::<sqlx::Postgres, Response>(
        "SELECT * FROM response ORDER BY response_time DESC LIMIT 100",
    )
    .fetch_all(&state.db)
    .await
    .unwrap_or_else(|e| {
        eprintln!("error occured in db {}", e);
        Vec::new()
    });

    let mut internal_server_errors = vec![];

    responses
        .iter()
        .for_each(|response| match response.status_code {
            500 => internal_server_errors.push(response),
            _ => (),
        });

    let percent_500 = (internal_server_errors.len() as f32 / responses.len() as f32) * 100_f32;

    match percent_500 {
        p if p >= 50.0 => HttpResponse::Ok().body(format!(
            "percentage of server errors: {}%: service is experiencing issues",
            percent_500
        )),
        p if p < 50.0 => HttpResponse::Ok().body(format!(
            "percentage of server errors: {}%: service is healthy",
            percent_500
        )),
        _ => HttpResponse::Ok().body(format!("error")),
    }
}

#[derive(Deserialize, Serialize, Debug)]

struct InteractionStats {
    post_stats: PostStats,
    dm_stats: DmStats,
    repost_stats: RepostStats,
    community_stats: CommunityStats,
    other_stats: OtherStats,
}
impl InteractionStats {
    fn new_interaction_stats() -> Self {
        Self {
            post_stats: PostStats::default(),
            dm_stats: DmStats::default(),
            repost_stats: RepostStats::default(),
            community_stats: CommunityStats::default(),
            other_stats: OtherStats::default(),
        }
    }
}

#[derive(Deserialize, Serialize, Debug, Default)]

struct PostStats {
    percent: String,
    total_number: u16,
}
#[derive(Deserialize, Serialize, Debug, Default)]

struct DmStats {
    percent: String,
    total_number: u16,
}
#[derive(Deserialize, Serialize, Debug, Default)]

struct RepostStats {
    percent: String,
    total_number: u16,
}
#[derive(Deserialize, Serialize, Debug, Default)]

struct CommunityStats {
    percent: String,
    total_number: u16,
}

#[derive(Deserialize, Serialize, Debug, Default)]

struct OtherStats {
    percent: String,
    total_number: u16,
}

pub async fn get_popular_traffic(state: Data<AppState>) -> impl Responder {
    let requests: Vec<Request> =
        sqlx::query_as::<sqlx::Postgres, Request>("SELECT * FROM request ")
            .fetch_all(&state.db)
            .await
            .unwrap_or_else(|e| {
                eprintln!("error occured in db: {}", e);
                Vec::new()
            });
    if requests.is_empty() {
        HttpResponse::Ok().body("");
    }

    let mut post_list: Vec<&Request> = vec![];
    let mut dm_list: Vec<&Request> = vec![];
    let mut repost_list: Vec<&Request> = vec![];
    let mut community_list: Vec<&Request> = vec![];
    let mut other_list: Vec<&Request> = vec![];
    let total_length = requests.len();
    requests.iter().for_each(|request| match &request.url {
        u if u.contains("post") => post_list.push(request),
        u if u.contains("dm") => dm_list.push(request),
        u if u.contains("repost") => repost_list.push(request),
        u if u.contains("community") => community_list.push(request),
        _ => other_list.push(request),
    });

    let mut combined_stats = InteractionStats::new_interaction_stats();

    combined_stats.post_stats = PostStats {
        percent: format!(
            "{}%",
            (post_list.len() as f32 / total_length as f32) * 100_f32
        ),
        total_number: post_list.len() as u16,
    };
    combined_stats.dm_stats = DmStats {
        percent: format!(
            "{}%",
            (dm_list.len() as f32 / total_length as f32) * 100_f32
        ),
        total_number: dm_list.len() as u16,
    };
    combined_stats.repost_stats = RepostStats {
        percent: format!(
            "{}%",
            (repost_list.len() as f32 / total_length as f32) * 100_f32
        ),
        total_number: repost_list.len() as u16,
    };
    combined_stats.community_stats = CommunityStats {
        percent: format!(
            "{}%",
            (community_list.len() as f32 / total_length as f32) * 100_f32
        ),
        total_number: community_list.len() as u16,
    };
    combined_stats.other_stats = OtherStats {
        percent: format!(
            "{}%",
            (other_list.len() as f32 / total_length as f32) * 100_f32
        ),
        total_number: other_list.len() as u16,
    };

    HttpResponse::Ok().json(combined_stats)
}

pub async fn restart_service() -> impl Responder {
    let script_path = "../src/restart.sh";

    let child = Command::new("setsid")
        .arg(script_path)
        .spawn()
        .expect("failed to execute script");
    println!("Started detached process with ID: {}", child.id());

    HttpResponse::Ok()
}
