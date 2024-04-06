# Use the official Rust image as a base
FROM rust:1.76 as builder

WORKDIR /telemetry

COPY ./Cargo.toml ./Cargo.toml
COPY ./Cargo.lock ./Cargo.lock
COPY ./.env ./.env

COPY ./src ./src

RUN cargo build --release

FROM debian:bookworm-slim
ARG APP=/usr/src/app

RUN apt-get update \
    && apt-get install -y openssl \
    && rm -rf /var/lib/apt/lists/*


COPY --from=builder /telemetry/target/release/more_simple_api ${APP}/app
WORKDIR ${APP}

ENTRYPOINT ["./app"]
EXPOSE 8080