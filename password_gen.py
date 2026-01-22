# password generator
from dataclasses import dataclass
import string
import secrets
from typing import List
import math

@dataclass
class PasswordOptions:
    length: int = 12
    include_lower: bool = True
    include_upper: bool = True
    include_digits: bool = True
    include_symbols: bool = False
    avoid_ambiguous: bool = True  

def _filter_ambiguous(chars: str) -> str:
    ambiguous = set("O0oIl1|`'\";:.,{}[]()<>")
    return "".join(ch for ch in chars if ch not in ambiguous)

def _build_charsets(opts: PasswordOptions) -> List[str]:
    sets = []
    if opts.include_lower:
        sets.append(string.ascii_lowercase)
    if opts.include_upper:
        sets.append(string.ascii_uppercase)
    if opts.include_digits:
        sets.append(string.digits)
    if opts.include_symbols:
        # choose a friendly, commonly allowed symbol set
        sets.append("!@#$%^&*_-+=?")
    if opts.avoid_ambiguous:
        sets = [_filter_ambiguous(s) for s in sets]
    # remove any empty sets (can happen after filtering)
    sets = [s for s in sets if s]
    return sets

# rating the strength of generated password
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
    
# calculating entropy
def calculate_entropy(password: str, pool_size: int) -> float:
    """
    Calculate password entropy (in bits).
    Formula: entropy = length * log2(pool_size)
    """
    return len(password) * math.log2(pool_size)

# generating password
def generate_password(opts: PasswordOptions) -> str:
    charsets = _build_charsets(opts)

    if opts.length < len(charsets):
        raise ValueError(f"Password length too short. Must be at least {len(charsets)} characters to include all sets.")
    
    if not any([opts.include_lower, opts.include_upper, opts.include_digits, opts.include_symbols]):
        raise ValueError("You must select at least one character type.")
    
    if not charsets:
        raise ValueError("Select at least one character type.")

    # ensure at least one char from each selected set
    pwd_chars = [secrets.choice(s) for s in charsets]

    # fill remaining with combined pool
    pool = "".join(charsets)
    remaining = opts.length - len(pwd_chars)
    pwd_chars += [secrets.choice(pool) for _ in range(remaining)]

    # shuffle securely
    secrets.SystemRandom().shuffle(pwd_chars)

    pwd = "".join(pwd_chars)
    print(f"Password Strength: {password_strength(pwd)}")

    # calculate entropy
    pool_size = len(pool)  # total available characters
    entropy_bits = calculate_entropy(pwd, pool_size)
    print(f"\nPassword Strength: {password_strength(pwd)}")
    print(f"Entropy: {entropy_bits:.2f} bits\n")

    # save the generated password in a file
    with open("generated_passwords.txt", "a") as f:
        f.write(pwd + f" | Entropy: {entropy_bits:.2f} bits\n")

    return pwd






