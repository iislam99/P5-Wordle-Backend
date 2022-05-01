#!/usr/bin/env python3
import collections
import contextlib
import sqlite3
import typing
from datetime import datetime

from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings

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
    user_id: int
    game_id: int
    num_guesses: int

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
    