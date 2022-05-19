import httpx
from collections import OrderedDict
from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings

class User(BaseModel):
    username: str

class Game(BaseModel):
    user_id: str
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
def game_guess(game_id: int, game: Game, response: Response):
    res = OrderedDict()

    # Ensure word is valid before making guess
    r = httpx.put('http://localhost:9999/validate/', json={"word": game.guess})
    valid_r = r.json()
    if valid_r.get("status", 0):
        if valid_r["status"] == "Invalid":
            return valid_r
    else:
        return valid_r
    
    # Get game
    r = httpx.post(
        'http://localhost:9999/get_game/', 
        json={
            "user_id": game.user_id,
            "game_id": game_id
        }
    )
    game_r = r.json()
    if game_r["status"] != "Valid":
        return game_r
    
    # Check if user has any guesses left
    if not game_r["remaining guesses"]:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"msg": "Error: No guesses remaining."}
    
    # Make guess; handles invalid user and game ids
    r = httpx.put(
        'http://localhost:9999/make_guess/', 
        json={
            "user_id": game.user_id,
            "game_id": game_id,
            "guess": game.guess
        }
    )
    guess_r = r.json()
    if "Success" not in guess_r["msg"]:
        return guess_r

    # Check guess
    r = httpx.put('http://localhost:9999/check/', json={"word": game.guess})
    guess_r = r.json()

    if guess_r["correct"]:
        res["status"] = "win"
        won = 1
    elif not game_r["remaining guesses"] - 1:
        res["status"] = "loss"
        won = 0
    else:
        correct = []
        present = []
        for i, pos in enumerate(guess_r["results"]):
            if pos == 2:
                correct.append(game.guess[i])
            elif pos == 1:
                present.append(game.guess[i])

        res["status"] = "incorrect"
        res["remaining"] = game_r["remaining guesses"] - 1
        res["letters"] = {"correct": correct, "present": present}
        return res
    
    # POST finished game data
    res["remaining"] = game_r["remaining guesses"] - 1
    r = httpx.post(
        'http://localhost:9999/finish/', 
        json={
            "user_id": game.user_id,
            "game_id": game_id,
            "guesses": 6 - res["remaining"],
            "won": won
        }
    )
    finish_r = r.json()
    if not finish_r.get("msg", 0):
        return finish_r
    elif "Successfully" not in finish_r["msg"]:
        return finish_r
    
    # Get player stats
    r = httpx.post('http://localhost:9999/stats/', json={"user_id": game.user_id})
    finish_r = r.json()
    res.update(finish_r)

    return res