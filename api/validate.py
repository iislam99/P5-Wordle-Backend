# Science Fiction Novel API - FastAPI Edition
#
# Adapted from "Creating Web APIs with Python and Flask"
# <https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask>.
#

import collections
import contextlib
#import logging.config
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


#def get_logger():
#    return logging.getLogger(__name__)


settings = Settings()
app = FastAPI()

#logging.config.fileConfig(settings.logging_config)

@app.post("/words/", status_code=status.HTTP_201_CREATED)
def validate_word(
    word_obj: Word, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    w = dict(word_obj)
    try:
        cur = db.execute(
            """
            SELECT COUNT(*) FROM ValidWords WHERE word = :word
            """,
            w
        )
        db.commit()
    except Exception:
        return {"data": "Failed to reach database"}

    res = cur.fetchall()
    return {"data": "Valid"} if res[0][0] > 0 else {"data": "Invalid"}

