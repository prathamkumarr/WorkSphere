from fastapi import HTTPException
from pydantic import BaseModel
import random
from fastapi import APIRouter

router = APIRouter()

CHOICES = ("rock", "paper", "scissors")
WIN_MAP = {"rock": "scissors", "paper": "rock", "scissors": "paper"}

class RPSRequest(BaseModel):
    rounds: int = 3
    moves: list[str] = []

def _normalize(user_in: str) -> str:
    s = user_in.strip().lower()
    aliases = {"r": "rock", "p": "paper", "s": "scissors"}
    if s in aliases:
        return aliases[s]
    if s in CHOICES:
        return s
    if s.startswith("r"): return "rock"
    if s.startswith("p"): return "paper"
    if s.startswith("s"): return "scissors"
    return s

def _round_result(player: str, cpu: str) -> int:
    if player == cpu:
        return 0
    return 1 if WIN_MAP[player] == cpu else -1

@router.get("/", tags=["Rock-Paper-Scissors"])
def play_rps():
    return {"message": "Welcome to rock-paper-scissors API"}

@router.post("/play_best_of",  tags=["Rock-Paper-Scissors"])
def play_best_of(request: RPSRequest):
    n_rounds = request.rounds
    player_moves = request.moves or []
    player_score = cpu_score = 0
    needed = (n_rounds // 2) + 1
    round_no = 1
    round_history = []
    last_player_move = None  

    while player_score < needed and cpu_score < needed:
        # saving player's old moves
        if len(player_moves) >= round_no:
            player = _normalize(player_moves[round_no - 1])
        else:
            player = random.choice(CHOICES)

        # CPU smart logic:
        if last_player_move:
            losing_move = WIN_MAP[last_player_move]
            # Avoid picking the losing move if possible
            cpu_choices = [c for c in CHOICES if c != losing_move]
        else:
            cpu_choices = CHOICES

        cpu = random.choice(cpu_choices)
        last_player_move = player  

        if player not in CHOICES:
            raise HTTPException(status_code=400, detail=f"Invalid move '{player}'.")

        # Determining round result
        result = _round_result(player, cpu)

        if result == 1:
            player_score += 1
        elif result == -1:
            cpu_score += 1

        round_history.append({
            "round": round_no,
            "player": player,
            "cpu": cpu,
            "result": "tie" if result == 0 else "player wins" if result == 1 else "cpu wins"
        })

        if player_score == needed or cpu_score == needed:
            break
        round_no += 1

    return {
        "total_rounds": n_rounds,
        "final_score": {"player": player_score, "cpu": cpu_score},
        "winner": "player" if player_score > cpu_score else "cpu",
        "round_history": round_history
    }

