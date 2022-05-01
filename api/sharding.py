#!/usr/bin/env python3

import sqlite3
import uuid
from pydantic import BaseSettings

class Settings(BaseSettings):
    stats_database: str
    games_1_database: str
    games_2_database: str
    games_3_database: str
    users_database: str
    logging_config: str

    class Config:
        env_file = ".env"

print("Beginning sharding...")

settings = Settings()

stats_conn = sqlite3.connect(settings.stats_database, detect_types=sqlite3.PARSE_DECLTYPES)
users_conn = sqlite3.connect(settings.users_database, detect_types=sqlite3.PARSE_DECLTYPES)
games_conn = [
    sqlite3.connect(settings.games_1_database, detect_types=sqlite3.PARSE_DECLTYPES),
    sqlite3.connect(settings.games_2_database, detect_types=sqlite3.PARSE_DECLTYPES),
    sqlite3.connect(settings.games_3_database, detect_types=sqlite3.PARSE_DECLTYPES)
]

stats_cur = stats_conn.cursor()
users_cur = users_conn.cursor()
games_cur = [i.cursor() for i in games_conn]


# Create new users table with GUID column in users db
# Copy users from stats db to users db into new users table
# Delete old users table in users db
# Rename new users table in users db to users
sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
id_to_uuid = {}
try:  
    users_cur.execute('DROP TABLE IF EXISTS users_new')
    users_cur.execute('''CREATE TABLE users_new (
                            user_id GUID PRIMARY KEY, 
                            username VARCHAR UNIQUE,
                            og_id INTEGER UNIQUE
                         )''')
    stats_cur.execute('SELECT * FROM users')
    users_list = stats_cur.fetchall()

    for row in users_list:
        guid = uuid.uuid4()
        user_data = (guid, row[1], row[0])
        users_cur.execute('INSERT INTO users_new VALUES (?,?,?)', user_data)
        id_to_uuid[row[0]] = guid

    users_cur.execute('DROP TABLE users')
    users_cur.execute('ALTER TABLE users_new RENAME TO users')
    users_conn.commit()

except Exception as e:
    print("Error: Failed to copy users and add GUID column. " + str(e))


# For each row in games table in stats db, assign row to games shard
try:
    # Replace tables in game shards for UUID compatibility
    for i in range(3):
        games_cur[i].execute('DROP TABLE IF EXISTS games')
        games_cur[i].execute('''
            CREATE TABLE games (
                user_id GUID,
                game_id INTEGER NOT NULL,
                finished DATE DEFAULT CURRENT_TIMESTAMP,
                guesses INTEGER,
                won BOOLEAN,
                PRIMARY KEY(user_id, game_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )''')
        games_cur[i].execute('CREATE INDEX games_won_idx ON games(won)')
        games_conn[i].commit()
except Exception as e:
    print("Failed to replace games tables.", str(e))

try:
    # Move game values from stats db to games shard based on uuid as shard key
    stats_cur.execute('SELECT * FROM games')
    games_list = stats_cur.fetchall()
    
    for g in games_list:
        guid = id_to_uuid[g[0]]
        shard = int(guid) % 3
        game_data = (guid, g[1], g[2], g[3], g[4])
        games_cur[shard].execute('INSERT INTO games VALUES (?,?,?,?,?)', game_data)

    for g in games_conn:
        g.commit()

except Exception as e:
    print("Failed to add values to games shards.", str(e))


for i in range(3):
    try:
        # Add wins views to shard
        games_cur[i].execute('DROP VIEW IF EXISTS wins')
        games_cur[i].execute('''
            CREATE VIEW wins
            AS
                SELECT
                    user_id,
                    COUNT(won)
                FROM
                    games
                WHERE
                    won = TRUE
                GROUP BY
                    user_id
                ORDER BY
                    COUNT(won) DESC
            ''')
        games_conn[i].commit()
    except Exception as e:
        print("Error: Failed to create wins view. " + str(e))

for i in range(3):
    try:
        # Add streaks view to shard
        games_cur[i].execute('DROP VIEW IF EXISTS streaks')
        games_cur[i].execute('''
            CREATE VIEW streaks
            AS
                WITH ranks AS (
                    SELECT DISTINCT
                        user_id,
                        finished,
                        RANK() OVER(PARTITION BY user_id ORDER BY finished) AS rank
                    FROM
                        games
                    WHERE
                        won = TRUE
                    ORDER BY
                        user_id,
                        finished
                ),
                groups AS (
                    SELECT
                        user_id,
                        finished,
                        rank,
                        DATE(finished, '-' || rank || ' DAYS') AS base_date
                    FROM
                        ranks
                )
                SELECT
                    user_id,
                    COUNT(*) AS streak,
                    MIN(finished) AS beginning,
                    MAX(finished) AS ending
                FROM
                    groups
                GROUP BY
                    user_id, base_date
                HAVING
                    streak > 1
                ORDER BY
                    user_id,
                    finished
            ''')
        games_conn[i].commit()
    except Exception as e:
        print("Error: Failed to create streaks view. " + str(e))

