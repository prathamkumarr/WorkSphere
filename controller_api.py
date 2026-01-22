from fastapi import FastAPI, HTTPException
from pwd_api import generate_password, PasswordOptions
from rps_api import play_best_of, RPSRequest

app = FastAPI(title="Main Controller API", version="1.0", description="unfied API for Password Generator and Rock-Paper-Scissors modules")

# enpoint to call password generator
@app.post("/run/password")
def run_password_generator(options: PasswordOptions):
    """
    Runs the password generator module.
    """
    try:
        result = generate_password(options)
        return {
            "module": "Password Generator",
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# endpoint to run best of n rounds rps game
@app.post("/run/rps-bestof")
def run_rps_bestof(request: RPSRequest):
    """
    Runs a 'best-of-N' match of Rock-Paper-Scissors.
    """
    try:
        result = play_best_of(request)
        return {
            "module": "Rock Paper Scissors",
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# endpoint for menu
@app.get("/")
def root_menu():
    return {
        "message": "Welcome to the Unified Module API 🎯",
        "available_modules": {
            "1": {"name": "Password Generator", "endpoint": "/run/password"},
            "2": {"name": "Rock-Paper-Scissors (Best Of)", "endpoint": "/run/rps-bestof"},
        },
        "note": "Send POST requests with proper JSON body to play or generate passwords!"
    }
