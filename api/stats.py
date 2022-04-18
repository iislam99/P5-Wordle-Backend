import collections
import contextlib
import sqlite3
import typing
from datetime import date

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
    guesses: int
    won: bool

def get_db():
    with contextlib.closing(sqlite3.connect(settings.stats_database)) as db:
        db.row_factory = sqlite3.Row
        yield db

settings = Settings()
app = FastAPI()

@app.post("/finish/", status_code=status.HTTP_200_OK)
def process_end(
    game: Game, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    today = date.today().strftime("%Y-%m-%d")
    try:
        cur = db.execute("SELECT * FROM games WHERE user_id = ? AND game_id = ?", (game.user_id, game.game_id))
        db.commit()
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"msg": "Error: Failed to reach database. " + str(e)}
    
    rows = cur.fetchall()
    if len(rows) != 0:
        return {"msg": "Game Already Finished"}
    try:
        cur = db.execute(
            """
            INSERT INTO games VALUES(?, ?, ?, ?, ?);
            """
            , (game.user_id, game.game_id, today, game.guesses, game.won))
        db.commit()
        return {"msg": "Successfully Posted Win/Loss"}
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"msg": "Error: Failed to insert into database. " + str(e)}

    return {"msg": "Failed to Post Win/Loss"}