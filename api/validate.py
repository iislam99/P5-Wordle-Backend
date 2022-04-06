import collections
import contextlib
import sqlite3
import typing

from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings


class Settings(BaseSettings):
    valid_words_database: str
    logging_config: str

    class Config:
        env_file = ".env"

class Word(BaseModel):
    word: str


def get_db():
    with contextlib.closing(sqlite3.connect(settings.valid_words_database)) as db:
        db.row_factory = sqlite3.Row
        yield db



settings = Settings()
app = FastAPI()


@app.post("/words/", status_code=status.HTTP_200_OK)
def validate_word(
    word_obj: Word, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    word = word_obj.word.lower() 
   
    if (len(word) != 5):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"msg": "Error: Incorrect word length"}

    try:
        cur = db.execute("SELECT COUNT(*) FROM ValidWords WHERE word = ?", word)
        db.commit()
    except Exception:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"msg": "Error: Failed to reach database"}

    word_exists = bool(cur.fetchall()[0][0])
    return {"msg": "Valid"} if word_exists else {"msg": "Invalid"}

