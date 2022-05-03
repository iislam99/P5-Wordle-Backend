#!/usr/bin/env python3
import collections
import contextlib
import sqlite3
import typing
import uuid
import typing

from datetime import datetime

from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings
from collections import OrderedDict

import redis
r = redis.Redis()

class Settings(BaseSettings):
    games_1_database: str
    games_2_database: str
    games_3_database: str
    users_database: str
    logging_config: str
    class Config:
        env_file = ".env"


class GameStart(BaseModel):
    og_id: int
    game_id: int

class GameGuess(BaseModel):
    og_id: int
    game_id: int
    guess: str

def get_db():
    #db dependency yields a connection to all tables store in a list
    with contextlib.closing(sqlite3.connect(settings.games_1_database)) as db1:
        db1.row_factory = sqlite3.Row
        with contextlib.closing(sqlite3.connect(settings.games_2_database)) as db2:
            db2.row_factory = sqlite3.Row
            with contextlib.closing(sqlite3.connect(settings.games_3_database)) as db3:
                db3.row_factory = sqlite3.Row
                with contextlib.closing(sqlite3.connect(settings.users_database)) as users:
                    users.row_factory = sqlite3.Row
                    yield [db1, db2, db3, users]

settings = Settings()
app = FastAPI()
@app.put("/start/", status_code=status.HTTP_200_OK)
def check(s: GameStart, response: Response, db: sqlite3.Connection = Depends(get_db)):
    try:
        cur = db[3].cursor()
        cur.execute("SELECT user_id FROM users WHERE og_id = ?", (s.og_id,))
        guid = cur.fetchall()[0][0]
        db[3].commit()
    except Exception as e:
        return {"msg": "Error: Failed to reach users. " + str(e)}
    
    shard = int(uuid.UUID(bytes_le=guid)) % 3
    
    try:
        cur = db[shard].cursor()
        cur.execute("SELECT * FROM games WHERE user_id = ? AND game_id = ?", (guid, s.game_id))
        temp = cur.fetchall()
        db[shard].commit()
    except Exception as e:
        return {"msg": "Error: Failed to reach game. " + str(e)}
    if len(temp) != 0 or len(r.hgetall(f"{guid},{s.game_id}")) != 0:
        return {"msg": "Error: Game already finished. "}
    guesses = {1:'',2:'',3:'',4:'',5:'',6:''}
    r.hmset(f"{guid},{s.game_id}", guesses)
    return {"msg": "Success: Game has been started"}

@app.put("/make_guess/", status_code=status.HTTP_200_OK)
def make_guess(s: GameGuess, response: Response, db: sqlite3.Connection = Depends(get_db)):
    try:
        cur = db[3].cursor()
        cur.execute("SELECT user_id FROM users WHERE og_id = ?", (s.og_id,))
        guid = cur.fetchall()[0][0]
        db[3].commit()
    except Exception as e:
        return {"msg": "Error: Failed to reach users. " + str(e)}
    
    shard = int(uuid.UUID(bytes_le=guid)) % 3
    
    val = r.hgetall(f"{guid},{s.game_id}")
    if len(val) == 0:
        return {"msg": "Error: Game does not exist. "}

    for k,v in val.items():
        if len(v) == 0:
            val[k] = s.guess
            r.hmset(f"{guid},{s.game_id}", val)
            return {"msg": "Success: Game has been inserted"}
    
    return {"msg": "Error: Only 6 guesses are allowed"}

@app.get("/get_game/", status_code=status.HTTP_200_OK)
def get_game(s: GameStart, response: Response, db: sqlite3.Connection = Depends(get_db)):
    try:
        cur = db[3].cursor()
        cur.execute("SELECT user_id FROM users WHERE og_id = ?", (s.og_id,))
        guid = cur.fetchall()[0][0]
        db[3].commit()
    except Exception as e:
        return {"msg": "Error: Failed to reach users. " + str(e)}
    
    shard = int(uuid.UUID(bytes_le=guid)) % 3
    
    val = r.hgetall(f"{guid},{s.game_id}")
    if len(val) == 0:
        return {"msg": "Error: Game does not exist. "}

    result = OrderedDict()
    guesses = OrderedDict()

    guess_count = 0
    for k,v in val.items():
        guess_num = int(k.decode("utf-8"))
        if len(v) != 0:
            guess_count += 1
            guesses[guess_num] = v.decode("utf-8")
        else:
           break
    
    result["Current Guesses"] = guesses
    result["Remaining Guesses"] = 6 - guess_count
    return result

    
