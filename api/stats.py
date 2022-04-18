import collections
import contextlib
import sqlite3
import typing
from datetime import date
from collections import OrderedDict

from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings


class Settings(BaseSettings):
    stats_database: str
    logging_config: str

    class Config:
        env_file = ".env"

class User(BaseModel):
    # user id can be fetched or provided depending on if the user knows their id
    user_id: int = None 
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
            INSERT INTO games VALUES(?, ?, ?, ?, ?)
            """
            , (game.user_id, game.game_id, today, game.guesses, game.won))
        # need to refresh views here but don't really know how
        # db.execute("EXECUTE sp_refreshview 'wins'")
        # db.execute("sp_refreshview 'streaks'")
        db.commit()
        return {"msg": "Successfully Posted Win"} if game.won else {"msg": "Successfully Posted Loss"}
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"msg": "Error: Failed to insert into database. " + str(e)}

    return {"msg": "Failed to Post Win/Loss"}

@app.get("/stats/", status_code=status.HTTP_200_OK)
def fetch_stats(
    user: User, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    today = date.today().strftime("%Y-%m-%d")
    cur_name = user.username
    cur_id = user.user_id
    if cur_id == 0:
        try:
            cur = db.execute("SELECT user_id FROM users WHERE username = ?", (cur_name,))
            cur_id = cur.fetchall()[0][0]
        except Exception as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"msg": "Error: Failed to reach users table. " + str(e)}
    result = OrderedDict()
    try:
        cur = db.execute("SELECT MAX(streak) FROM streaks WHERE user_id = ?", (cur_id,))
        maxStreak = cur.fetchall()[0][0]
        
        # for current streak, we need to check if there is an existing streak
        # where the finished date is equal to today's date
        cur = db.execute("SELECT streak FROM streaks WHERE user_id = ? AND ending = ?", (cur_id,today))
        
        curStreak = cur.fetchall()
        curStreak = curStreak[0][0] if len(curStreak) != 0 else 0
        
        
        cur = db.execute("SELECT COUNT(game_id) FROM games WHERE user_id = ?", (cur_id,))
        games_played = cur.fetchall()[0][0]
        
        cur = db.execute("SELECT [COUNT(won)] FROM wins WHERE user_id = ?", (cur_id,))
        games_won = cur.fetchall()[0][0]
        
        cur = db.execute("SELECT AVG(guesses) FROM games WHERE user_id = ?", (cur_id,))
        avg_guess = cur.fetchall()[0][0]

        cur = db.execute("SELECT guesses, COUNT(game_id) FROM games WHERE user_id = ? GROUP BY guesses", (cur_id,))
        temp = cur.fetchall()
        # stores list of tuples such as [(1, 3), (2, 5)...]
        guess_distribution = [(guess, temp[guess-1][1]) for guess in range(1,7)]
        db.commit()
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"msg": "Error: Failed to load data. " + str(e)}
    result["currentStreak"] = curStreak
    result["maxStreak"] = maxStreak
    tempDict = OrderedDict()
    for item in guess_distribution:
        tempDict[f"{item[0]}"] = item[1] 
    result["guesses"] = tempDict
    result["winPercentage"] = round(games_won/games_played * 100)
    result["gamesPlayed"] = games_played
    result["gamesWon"] = games_won
    result["averageGuesses"] = round(avg_guess)
    return result

@app.get("/top_wins/", status_code=status.HTTP_200_OK)
def fetch_top_wins(
    response: Response, db: sqlite3.Connection = Depends(get_db)
):
    result = OrderedDict()
    try: 
        cur = db.execute("SELECT * FROM wins LIMIT 10",)
        top_table = cur.fetchall()
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"msg": "Error: Failed to reach wins table. " + str(e)}
    user_ids = []
    for row in top_table:
        user_ids.append(row[0])
    usernames =[]
    try: 
        for i in user_ids:
            cur = db.execute("SELECT username FROM users WHERE user_id = ?", (i,))
            usernames.append(cur.fetchall()[0][0])
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"msg": "Error: Failed to reach users table. " + str(e)}
    users = []
    for i in range(10):
        temp = OrderedDict()
        temp["username"] = usernames[i]
        temp["user_id"] = user_ids[i]
        users.append(temp)
    result["Users"] = users
    return result

@app.get("/longest_streak/", status_code=status.HTTP_200_OK)
def fetch_longest_streaks(
    response: Response, db: sqlite3.Connection = Depends(get_db)
):
    result = OrderedDict()
    try: 
        cur = db.execute("SELECT user_id, streak FROM streaks ORDER BY streak DESC LIMIT 10",)
        top_table = cur.fetchall()
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"msg": "Error: Failed to reach wins table. " + str(e)}
    user_ids = []
    for row in top_table:
        user_ids.append(row[0])
    usernames =[]
    try: 
        for i in user_ids:
            cur = db.execute("SELECT username FROM users WHERE user_id = ?", (i,))
            usernames.append(cur.fetchall()[0][0])
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"msg": "Error: Failed to reach users table. " + str(e)}
    users = []
    for i in range(10):
        temp = OrderedDict()
        temp["username"] = usernames[i]
        temp["user_id"] = user_ids[i]
        users.append(temp)
    result["Users"] = users
    return result