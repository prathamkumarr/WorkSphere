# rock-paper-scissors
import random

CHOICES = ("rock", "paper", "scissors")
WIN_MAP = {
    "rock": "scissors",     
    "paper": "rock",       
    "scissors": "paper"     
}

# normalizing user inputs to required keywords
def _normalize(user_in: str) -> str:
    """
    normalize user input to 'rock'|'paper'|'scissors'.
    accepts full words, single-letter aliases (r/p/s), and common prefixes.
    """
    s = user_in.strip().lower()
    if not s:
        return s
    
    # exact shortcuts
    aliases = {"r": "rock", "p": "paper", "s": "scissors"}
    if s in aliases:
        return aliases[s]
    
    # exact full words
    if s in ("rock", "paper", "scissors"):
        return s
    
    # prefix-friendly: 'ro', 'roc' => rock etc.
    if s.startswith("r"): return "rock"
    if s.startswith("p"): return "paper"
    if s.startswith("s"): return "scissors"
    return s

def _round_result(player: str, cpu: str) -> int:
    """returns +1 if player wins, -1 if cpu wins, 0 tie"""
    if player == cpu:
        return 0
    return 1 if WIN_MAP.get(player) == cpu else -1

def color(text, code):
    return f"\033[{code}m{text}\033[0m"

GREEN = "32"
RED = "31"
YELLOW = "33"
CYAN = "36"

def play_rps_best_of(n_rounds: int = 5):
    """
    Play Rock-Paper-Scissors best-of-n rounds.
    n_rounds must be a positive odd number (e.g. 3, 5, 7).
    """

    if n_rounds % 2 == 0 or n_rounds <= 0:
        raise ValueError("Use a positive odd number (e.g., 3, 5, 7).")

    print("\n=== Rock-Paper-Scissors ===")
    print("Type rock/paper/scissors or r/p/s. Type 'q' to quit.\n")

    player_score = 0
    cpu_score = 0
    needed = (n_rounds // 2) + 1

    round_no = 1
    last_player_move = None

    while player_score < needed and cpu_score < needed:
        user_in = input(f"Round {round_no} - your move: ")
        if user_in.strip().lower() == "q":
            print("You bailed  — match ended early.")
            return
        player = _normalize(user_in)
        if player not in CHOICES:
            print("Invalid input. Try rock/paper/scissors (or r/p/s).")
            continue

        if last_player_move:
        # CPU avoids repeating the losing choice
            if WIN_MAP[last_player_move] in CHOICES:
                cpu_choices = [c for c in CHOICES if c != WIN_MAP[last_player_move]]
            else:
                cpu_choices = CHOICES
        else:
            cpu_choices = CHOICES

        cpu = random.choice(cpu_choices)
        last_player_move = player

        res = _round_result(player, cpu)

        if res == 0:
            print(color(f"Tie! You: {player} | CPU: {cpu} | Score {player_score}-{cpu_score}", YELLOW))
        elif res == 1:
            player_score += 1
            print(color(f"You win the round! {player} > {cpu} | Score {player_score}-{cpu_score}", GREEN))
        else:
            cpu_score += 1
            print(color(f"CPU wins the round! {cpu} > {player} | Score {player_score}-{cpu_score}", RED))

        round_no += 1

    if player_score > cpu_score:
        print(color(f"You won the match {player_score}-{cpu_score}! GG!", GREEN))
    else:
        print(color(f"CPU won the match {cpu_score}-{player_score}. Rematch?", RED))

    # score board
    print(color("\n--- Final Scoreboard ---", CYAN))
    print(color(f"You: {player_score}", GREEN))
    print(color(f"CPU: {cpu_score}", RED))

    again = input("\nPlay again? (y/N): ").strip().lower()
    if again.startswith("y"):
        play_rps_best_of(n_rounds)
    else:
        print("Thanks for playing!")

   

        