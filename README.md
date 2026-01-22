# WorkSphere 

WorkSphere is a Python-based desktop work management application designed for managers and individuals to organize tasks, manage employees, and take productivity breaks using built-in games.

This project combines a Tkinter frontend with a FastAPI backend, following a modular and scalable architecture.

---

## Features

### Task Management
- Add, edit, delete tasks
- Set priorities (Low, Medium, High)
- Mark tasks as completed
- Persistent local storage (JSON)

### Employee Management
- Add, update, delete employees
- SQLite database storage
- Separate API layer

### Games (Productivity Breaks)
- Detective Guess Game (API-based)
- Rock Paper Scissors Game

### Utilities
- Password generator
- File manager
- Modular controller system

---

## Project Architecture

WorkSphere/

- run_app.py # App launcher (frontend + backend)
- main.py # FastAPI backend entry point
- main_app.py # Tkinter frontend

- WorkSphere/ # API modules
- detective_api.py
- employee_api.py
- todo_api.py
- controller_api.py
- Games
- python_detective_game.py
- rps.py

- Utilities
- password_gen.py
- file_manager_api.py


---

## Tech Stack

- Python 3.12
- Tkinter (Desktop UI)
- FastAPI (Backend APIs)
- SQLite
- REST APIs
- Modular OOP design