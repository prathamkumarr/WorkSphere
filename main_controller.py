# main controller
from password_gen import generate_password, PasswordOptions
from rps import play_rps_best_of

def menu():
    print("\n---Modules---")
    print("1. Password Generator")
    print("2. Rock-Paper-Scissors")
    print("3. Exit")

def run_password_generator():
    try:
        length = int(input("Password length (e.g., 12): ").strip() or "12")
        include_lower = input("Include lowercase? (y/N): ").lower().startswith("y")
        include_upper = input("Include uppercase? (y/N): ").lower().startswith("y")
        include_digits = input("Include digits?   (y/N): ").lower().startswith("y")
        include_symbols = input("Include symbols?  (y/N): ").lower().startswith("y")
        avoid_ambiguous = input("Avoid ambiguous chars (O0Il1)? (y/N): ").lower().startswith("y")

        opts = PasswordOptions(
            length=length,
            include_lower=include_lower,
            include_upper=include_upper,
            include_digits=include_digits,
            include_symbols=include_symbols,
            avoid_ambiguous=avoid_ambiguous
        )
        pwd = generate_password(opts)
        print(f"\nYour password: {pwd}\n")
    except ValueError as e:
        print(f"Error: {e}")

def run_rps():
    try:
        n = int(input("Best of how many rounds? (odd number, e.g., 5): ").strip() or "5")
        play_rps_best_of(n)
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    while True:
        menu()
        choice = input("Pick 1/2/3: ").strip()
        if choice == "1":
            run_password_generator()
        elif choice == "2":
            run_rps()
        elif choice == "3":
            print("bye!")
            break
        else:
            print("Invalid choice. Try again.")
