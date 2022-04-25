DROP TABLE IF EXISTS users;

CREATE TABLE users(
    user_id INTEGER,
    username VARCHAR UNIQUE
);