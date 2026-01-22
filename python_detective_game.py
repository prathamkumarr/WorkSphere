# Python Detective Game
import random

def guess_the_number():
    hidden_number = random.randint(1, 100)
    attempts = 0 
    max_attempts = 15

    print("Welcome, Detective! your mission: find the hidden number between 1 and 100.")
    print(f"you have {max_attempts} attempts to solve the case.") 

    # starting guessing loop
    while attempts < max_attempts:
        try:
            guess = int(input("Enter your guess (1-100): "))
        except ValueError:
            print("Please enter a valid number!")
            continue
  
        if guess < 1 or guess > 100:
            print("number must be between 1 and 100!")
            continue

        attempts += 1
        
        if attempts == 10:
            print(f"Reminder: You have already used {attempts} attempts.")
            print(f"Only {max_attempts - attempts} attempts left, Detective! be careful.")

        # giving feedback regarding guesses
        if guess < hidden_number:
            print("Too low, try again.")
        elif guess > hidden_number:
            print("Too high, try again.")
        else:
            print(f"Correct! The hidden number was {hidden_number}. Case closed, Detective!")
            print(f"Case closed in {attempts} attempts.")
            break

    else:
        print(f"Mission failed, Detective! the hidden number was {hidden_number}.\n")

# replay option
while True:
    guess_the_number()
    again = input("Play again? (y/n): ").lower()
    if again != "y":
        print("Detective leaving, goodbye!")
        break