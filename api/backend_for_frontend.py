import httpx
from collections import OrderedDict
from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings

class User(BaseModel):
    username: str

app = FastAPI()

@app.post("/game/new/", status_code=status.HTTP_200_OK)
def new_game(user: User, response: Response):
    res = OrderedDict()
    r = httpx.put('http://localhost:9999/start/', json={"username": user.username})
    res.update(r.json())
    return res

@app.post("/game/{game_id}/", status_code=status.HTTP_200_OK)
def game_guess(user: User, response: Response):
    pass