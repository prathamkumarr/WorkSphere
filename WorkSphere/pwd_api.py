from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import string, secrets, math
from collections import Counter
import math

router = APIRouter()

app = FastAPI(title="Password Generator API", version="1.0")

# data model
class PasswordOptions(BaseModel):
    length: int = 12
    include_lower: bool = True
    include_upper: bool = True
    include_digits: bool = True
    include_symbols: bool = False
    avoid_ambiguous: bool = True

# helper functions
def _filter_ambiguous(chars: str) -> str:
    ambiguous = set("O0oIl1|`'\";:.,{}[]()<>")
    return "".join(ch for ch in chars if ch not in ambiguous)

def _build_charsets(opts: PasswordOptions):
    sets = []
    if opts.include_lower:
        sets.append(string.ascii_lowercase)
    if opts.include_upper:
        sets.append(string.ascii_uppercase)
    if opts.include_digits:
        sets.append(string.digits)
    if opts.include_symbols:
        sets.append("!@#$%^&*_-+=?")
    if opts.avoid_ambiguous:
        sets = [_filter_ambiguous(s) for s in sets]
    sets = [s for s in sets if s]
    return sets

def password_strength(password: str) -> str:
    length = len(password)
    score = 0
    if any(c.islower() for c in password): score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in "!@#$%^&*_-+=?" for c in password): score += 1
    if length >= 12: score += 1

    if score <= 2:
        return "Weak"
    elif score == 3:
        return "Medium"
    else:
        return "Strong"

def calculate_entropy(password: str, pool_size: int) -> float:
    # Shannon entropy of the actual password
    counts = Counter(password)
    probs = [v / len(password) for v in counts.values()]
    shannon = -sum(p * math.log2(p) for p in probs)

    # theoretical max entropy per char (based on pool size)
    theoretical = math.log2(pool_size)

    # Use the lower of both to stay mathematically valid
    return len(password) * min(shannon, theoretical)


# function password generator
def generate_password_internal(opts: PasswordOptions) -> dict:
    charsets = _build_charsets(opts)

    if opts.length < len(charsets):
        raise HTTPException(status_code=400, detail=f"Password length too short. Must be at least {len(charsets)} characters.")
    if not any([opts.include_lower, opts.include_upper, opts.include_digits, opts.include_symbols]):
        raise HTTPException(status_code=400, detail="You must select at least one character type.")
    if not charsets:
        raise HTTPException(status_code=400, detail="Select at least one character type.")

    pwd_chars = [secrets.choice(s) for s in charsets]
    pool = "".join(charsets)
    remaining = opts.length - len(pwd_chars)
    pwd_chars += [secrets.choice(pool) for _ in range(remaining)]
    secrets.SystemRandom().shuffle(pwd_chars)

    pwd = "".join(pwd_chars)
    entropy_bits = calculate_entropy(pwd, len(pool))

    # save in file
    with open("generated_passwords.txt", "a") as f:
        f.write(pwd + f" | Entropy: %.2f bits\n" % entropy_bits)

    return {
        "password": pwd,
        "strength": password_strength(pwd),
        "entropy_bits": round(entropy_bits, 2)
    }

@router.get("/", tags=["Password Generator"])
def root_password_api():
    return {"message": "Welcome to Password Generator API"}

# endpoint to generate password
@router.post("/generate_password")
def api_generate_password(options: PasswordOptions):
    """
    generate a strong password based on user options.
    """
    result = generate_password_internal(options)
    return result
