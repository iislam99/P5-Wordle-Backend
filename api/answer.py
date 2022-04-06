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
from datetime import datetime

from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings


class Settings(BaseSettings):
    answers_database: str
    logging_config: str

    class Config:
        env_file = ".env"

class Word(BaseModel):
    word: str

def get_db():
    with contextlib.closing(sqlite3.connect(settings.answers_database)) as db:
        db.row_factory = sqlite3.Row
        yield db


#def get_logger():
#    return logging.getLogger(__name__)


settings = Settings()
app = FastAPI()

#logging.config.fileConfig(settings.logging_config)

@app.post("/answer/", status_code=status.HTTP_201_CREATED)
def answer(
    word_obj: Word, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    word = word_obj.word.lower()

    epoch = datetime(2022, 4, 4, 0, 0, 0)

    diff = datetime.now() - epoch
    day = diff.days

    try:
        cur = db.execute(
            """
            SELECT word FROM Answers WHERE id = ?
            """,
            (day,)
        )
        db.commit()
    except Exception:
        return {"data": "Failed to reach database"}

    todaysWord = cur.fetchall()[0][0]
    
    freq_map = {}
    for c in todaysWord:
        if c not in freq_map:
            freq_map[c] = 1
        else:
            freq_map[c] += 1

    results = [None] * len(word)

    for i,c in enumerate(word):
        if c not in results:
            results[i] = 0
        if c in freq_map and freq_map[c] > 0:
            freq_map[c] -= 1
            if word[i] == todaysWord[i]:
                results[i] = 2
            else:
                results[i] = 1

    return {"results": results}
