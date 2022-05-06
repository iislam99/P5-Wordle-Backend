#!/usr/bin/env python3

from collections import OrderedDict
from pydantic import BaseSettings
import sqlite3
import redis
import uuid
from datetime import datetime
now = datetime.now()
print("Cron Log:",now)
print("Adding views to Redis database...")

class Settings(BaseSettings):
    games_1_database: str
    games_2_database: str
    games_3_database: str
    users_database: str
    logging_config: str

    class Config:
        env_file = ".env"

sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)

settings = Settings()

db = [
    sqlite3.connect(settings.games_1_database),
    sqlite3.connect(settings.games_2_database),
    sqlite3.connect(settings.games_3_database),
    sqlite3.connect(settings.users_database)
]

for i in db:
    i.row_factory = sqlite3.Row

r = redis.Redis()

# Wins View

# Takes the the top 10 wins from each shard and appends it to a list
top_table = []
for shard in range(3):
    try: 
        cur = db[shard].cursor()
        cur.execute("SELECT * FROM wins LIMIT 10")
        vals = cur.fetchall()
        for row in vals:
            top_table.append(row)
    except Exception as e:
        print("Error: Failed to reach wins view. " + str(e))

# Sorts top 30 users from across shards
top_table.sort(reverse=True, key=lambda row: row[1])
user_ids = []
num_wins = []
for row in top_table:
    user_ids.append(row[0])
    num_wins.append(row[1])

usernames = []
try: 
    for i in user_ids:
        cur = db[3].cursor()
        cur.execute("SELECT username FROM users WHERE user_id = ?", (i,))
        name = cur.fetchall()[0][0]
        usernames.append(name)
except Exception as e:
    print("Error: Failed to reach users table. " + str(e))

users = []
for i in range(len(usernames)):
    r.zadd("Wins", {usernames[i]: num_wins[i]})

# print("\nWins:")
# for key, score in r.zrevrange("Wins", 0, -1, withscores=True):
#     print(key.decode("utf-8"), score)


# Streaks View

# Takes the the top 10 streaks from each shard and appends it to a list
top_table = []
for shard in range(3):
    try: 
        cur = db[shard].cursor()
        cur.execute("SELECT user_id, streak FROM streaks ORDER BY streak DESC LIMIT 10")
        vals = cur.fetchall()
        for row in vals:
            top_table.append(row)
    except Exception as e:
        print("Error: Failed to reach streaks view. " + str(e))

# Sorts top 30 users from across shards
top_table.sort(reverse=True, key=lambda row: row[1])
user_ids = []
num_streaks = []
for row in top_table:
    user_ids.append(row[0])
    num_streaks.append(row[1])

usernames =[]
try: 
    for i in user_ids:
        cur = db[3].cursor()
        cur.execute("SELECT username FROM users WHERE user_id = ?", (i,))
        usernames.append(cur.fetchall()[0][0])
except Exception as e:
    print("Error: Failed to reach users table. " + str(e))

for i in range(len(usernames)):
    r.zadd("Streaks", {usernames[i]: num_streaks[i]})

# print("\nStreaks:")
# count = 0
# for key, score in r.zrevrange("Streaks", 0, 9, withscores=True):
#     print(count, key.decode("utf-8"), score)
#     count += 1