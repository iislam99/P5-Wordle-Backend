import collections
import contextlib
import sqlite3
import typing

from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings

class Settings(BaseSettings):
    stats_database: str
    logging_config: str

    class Config:
        env_file = ".env"

class User(BaseModel):
    user_id: int
    username: str

class Game(BaseModel):
    user_id: int
    game_id: int
    finished: datetime
    guesses: int
    won: bool

def get_db():
    with contextlib.closing(sqlite3.connect(settings.answers_database)) as db:
        db.row_factory = sqlite3.Row
        yield db

settings = Settings()
app = FastAPI()

@app.post("/finished/", status_code=status.HTTP_200_OK)
def process_end(
    game_obj: Game, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    pass