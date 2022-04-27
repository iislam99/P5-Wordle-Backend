PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS games;

CREATE TABLE games(
    user_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    finished DATE DEFAULT CURRENT_TIMESTAMP,
    guesses INTEGER,
    won BOOLEAN,
    PRIMARY KEY(user_id, game_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

PRAGMA analysis_limit=1000;
PRAGMA optimize;