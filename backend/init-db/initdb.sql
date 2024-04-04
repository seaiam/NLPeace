--CREATE USER more_simple_api_user WITH PASSWORD 'pwd';
--CREATE DATABASE telemetry_db;
--GRANT ALL PRIVILEGES ON DATABASE telemetry_db TO more_simple_api_user;

CREATE TABLE request (
    request_id UUID PRIMARY KEY,
    user_id int,
    request_body TEXT,
    request_time TIMESTAMP WITH TIME ZONE,
    url TEXT
);

create table response (
 	response_id UUID PRIMARY KEY,
 	user_id int,
	status_code int,
	response_time TIMESTAMPTZ

);
