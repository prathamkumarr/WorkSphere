# to-do list manager
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import json

router = APIRouter()

# Pydantic Models 
class Task(BaseModel):
    task: str
    priority: str = "Medium"
    completed: bool = False

def save_tasks(filename="tasks.json"):
    with open(filename, "w") as f:
        json.dump(tasks, f, indent=4)

def load_tasks(filename="tasks.json"):
    global tasks
    try:
        with open(filename, "r") as f:
            tasks = json.load(f)
    except FileNotFoundError:
        tasks = []

tasks = []
load_tasks()

@router.get("/welcome", tags=["To-Do List Manager"])
def welcome():
    return {"message": "Welcome to To-Do List Manager API!"}

# endpoint to add task
@router.post("/add", tags=["To-Do List Manager"])
def add_task(task: Task):
    tasks.append(task.model_dump())
    save_tasks()
    return {"message": "Task added successfully!", "task": task.model_dump()}

# endpoint to view task
@router.get("/", tags=["To-Do List Manager"])
def view_tasks():
    if not tasks:
        return {"message": "No tasks in the list."}
    return tasks

# endpoint to delete task
@router.delete("/delete/{task_number}", tags=["To-Do List Manager"])
def delete_task(task_number: int):
    if 0 < task_number <= len(tasks):
        removed = tasks.pop(task_number - 1)
        save_tasks()
        return {"message": f"Removed: {removed['task']}"}
    raise HTTPException(status_code=404, detail="Invalid task number!")

# endpoint to edit task
@router.put("/edit/{task_number}", tags=["To-Do List Manager"])
def edit_task(task_number: int, new_task: str, new_priority: str = "Medium"):
    if 0 < task_number <= len(tasks):
        tasks[task_number - 1]["task"] = new_task
        tasks[task_number - 1]["priority"] = new_priority.capitalize()
        save_tasks()
        return {"message": f"Updated Task #{task_number} → {new_task}"}
    raise HTTPException(status_code=404, detail="Invalid task number!")

# endpoint to mark as completed a task
@router.put("/complete/{task_number}", tags=["To-Do List Manager"])
def mark_complete(task_number: int):
    if 0 < task_number <= len(tasks):
        tasks[task_number - 1]["completed"] = True
        save_tasks()
        return {"message": f"'{tasks[task_number - 1]['task']}' marked as completed!"}
    raise HTTPException(status_code=404, detail="Invalid task number!")

# endpoint to set priority of a task
@router.put("/priority/{task_number}", tags=["To-Do List Manager"])
def set_priority(task_number: int, new_priority: str):
    if 0 < task_number <= len(tasks):
        new_priority = new_priority.capitalize()
        if new_priority not in ["High", "Medium", "Low"]:
            new_priority = "Medium"
        tasks[task_number - 1]["priority"] = new_priority
        save_tasks()
        return {"message": f"Priority set to {new_priority} for '{tasks[task_number - 1]['task']}'"}
    raise HTTPException(status_code=404, detail="Invalid task number!")



