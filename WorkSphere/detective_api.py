# Python Detective Game

from fastapi import HTTPException
import random
from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter()

class GuessInput(BaseModel):
    guess: int

game_state = {
    "hidden_number": None,
    "attempts": 0,
    "max_attempts": 15,
    "game_over": False
}

def reset_game_state():
    game_state["hidden_number"] = random.randint(1, 100)
    game_state["attempts"] = 0
    return {
        "message": "Game reset successfully! A new number has been chosen between 1 and 100."
    }

@router.get("/", tags=["Detective Game"])
def play_detective():
    return {"message": "Welcome to detective API"}

# endpoint for starting the game
@router.post("/start")
def start_game():
    game_state["hidden_number"] = random.randint(1, 100)
    game_state["attempts"] = 0
    return {
        "message": "Game started! Detective, your mission is to find the hidden number between 1 and 100.",
        "max_attempts": game_state["max_attempts"]
    }

# endpoint for making a guess
@router.post("/guess", tags=["Detective Game"])
def make_guess(data: GuessInput):
    if game_state["hidden_number"] is None:
        # Auto-reset the game if not started yet
        reset_game_state()

    if game_state["game_over"]:
        return {"message": "The game is already over! Please start a new one.", "status": "Game Over"}

    guess = data.guess
    game_state["attempts"] += 1
    attempts = game_state["attempts"]

    if attempts > game_state["max_attempts"]:
        game_state["game_over"] = True
        return {
            "message": f"Mission failed, Detective! The hidden number was {game_state['hidden_number']}.",
            "status": "Failed"
        }

    # checking range
    if guess < 1 or guess > 100:
        return {"message": "Number must be between 1 and 100!"}

    # comparing logic
    if guess < game_state["hidden_number"]:
        return {
            "message": "Too low, try again.",
            "attempts_left": game_state["max_attempts"] - attempts,
            "status": "In Progress"
        }
    elif guess > game_state["hidden_number"]:
        return {
            "message": "Too high, try again.",
            "attempts_left": game_state["max_attempts"] - attempts,
            "status": "In Progress"
        }
    else:
        game_state["game_over"] = True
        return {
            "message": f"Correct! The hidden number was {game_state['hidden_number']}. Case closed, Detective!",
            "attempts_used": attempts,
            "status": "Success"
        }


# endpoint for checking status of attempts
@router.get("/status")
def attempt_status():
    if game_state["game_over"]:
        return {
            "status": "Game Over",
            "message": f"Game ended. Hidden number was {game_state['hidden_number']}.",
            "attempts_used": game_state["attempts"],
            "attempts_left": 0
        }

    return {
        "status": "In Progress",
        "attempts_used": game_state["attempts"],
        "attempts_left": game_state["max_attempts"] - game_state["attempts"]
    }

# endpoint for resetting/restarting the game
@router.post("/reset", tags=["Detective Game"])
def reset_game():
    """
    Resets the game — new hidden number and attempts reset.
    """
    game_state["hidden_number"] = random.randint(1, 100)
    game_state["attempts"] = 0
    game_state["game_over"] = False
    return {
        "message": "New case assigned, Detective! Guess the new number between 1 and 100.",
        "status": "Ready",
        "attempts_left": game_state["max_attempts"],
        "attempts_used": 0
    }




