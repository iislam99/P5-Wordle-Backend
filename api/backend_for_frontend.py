import httpx
from collections import OrderedDict
from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings

class User(BaseModel):
    username: str

class Game(BaseModel):
    user_id: str,
    guess: str

app = FastAPI()

@app.post("/game/new/", status_code=status.HTTP_200_OK)
def new_game(user: User, response: Response):
    res = OrderedDict()
    
    # Retrieving game information
    r = httpx.put('http://localhost:9999/start/', json={"username": user.username})
    res.update(r.json())

    # If game in progress
    if res["status"] == "in-progress":
        guesses = [v for k,v in res["guesses"].items() if v != ""]
        remaining = 6 - len(guesses)
        correct = ['']*5
        present = []

        # Create frequency map of correct answer
        r = httpx.put('http://localhost:9999/check/', json={"word": "words"})
        answer = r.json()["word_of_the_day"]
        ans_map = {}
        for c in answer:
            if c in ans_map:
                ans_map[c] += 1
            else:
                ans_map[c] = 1
        ans_map_2 = ans_map.copy()

        # Find correct and present letters for each guess
        for word in guesses:
            r = httpx.put('http://localhost:9999/check/', json={"word": word})
            data = r.json()
            if data["correct"]:
                correct = [c for c in word]
                present = []
                break
            else:
                for i,c in enumerate(word):
                    # If letter in correct spot
                    if data["results"][i] == 2 and correct[i] != c:
                        correct[i] = c
                        ans_map_2[c] -= 1
                        if c in present:
                            present.remove(c)

                    # If letter is in wrong spot   
                    elif data["results"][i] == 1:
                        present.append(c)
                        if ans_map_2[c] > 0:
                            ans_map_2[c] -= 1

                    # Ensuring no extra letters in present array
                    if c in ans_map:
                        if correct.count(c) == ans_map[c]:
                            while c in present:
                                present.remove(c)
                        else:
                            while correct.count(c) + present.count(c) > ans_map[c]:
                                present.remove(c)
        correct = [c for c in correct if c != '']

        res["remaining"] = remaining
        res["guesses"] = guesses
        res["letters"] = {"correct": correct, "present": present}

    return res

@app.post("/game/{game_id}/", status_code=status.HTTP_200_OK)
def game_guess(user: User, response: Response):
    pass