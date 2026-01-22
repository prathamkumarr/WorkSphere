# To-Do List Manager

# function to add task
def add_task():
    task_input = input("Enter task(s), comma separated: ")
    task_list = [t.strip() for t in task_input.split(",")]
    for i, t in enumerate(task_list, start=1):
        tasks.append({"task": t, "priority": "Medium", "completed": False})
        print(f"{i}. {t} added to the list!")
    save_tasks()

# function to view tasks
def view_tasks():
    if not tasks:
        print("No tasks in the list.")
    else:
        print("\nYour Tasks:")
        for i, t in enumerate(tasks, start=1):
            status = "done" if t.get("completed", False) else "not done yet"
            name = t.get("task", "<untitled>")
            priority = t.get("priority", "Medium").capitalize()
            print(f"{i}. {name}  [{priority}]  {status}")
        print()

# function to delete task
def delete_task(task_number):
    if 0 < task_number <= len(tasks):
        removed = tasks.pop(task_number - 1)
        print(f"{removed['task']} removed from the list!")
        save_tasks()
    else:
        print("Invalid task number!")

# function to edit a task
def edit_task(task_number, new_task, new_priority):
    if 0 < task_number <= len(tasks):
        tasks[task_number - 1]["task"] = new_task
        tasks[task_number - 1]["priority"] = new_priority
        print(f"Task updated successfully!")
        save_tasks()
    else:
        print("Invalid task number!")

# function to mark a task as read
def mark_completed(task_number):
    if 0 < task_number <= len(tasks):
        tasks[task_number - 1]["completed"] = True
        print(f"{tasks[task_number - 1]['task']} marked as completed!")
        save_tasks()
    else:
        print("Invalid task number!")

# function to set priority
def set_priority(task_number, new_priority):
    new_priority = new_priority.capitalize() 
    if new_priority not in ["High", "Medium", "Low"]:
        print("Invalid priority! Defaulting to Medium.")
        new_priority = "Medium"

    if 0 < task_number <= len(tasks):
        tasks[task_number - 1]["priority"] = new_priority
        print(f"Priority for '{tasks[task_number - 1]['task']}' updated to {new_priority}!")
        save_tasks()
    else:
        print("Invalid task number!")

# function to save tasks
def save_tasks(filename="tasks.json"):
    with open(filename, "w") as f:
        json.dump(tasks, f, indent=4)
    print("Tasks saved successfully!")

# function to load tasks
def load_tasks(filename="tasks.json"):
    global tasks
    try:
        with open(filename, "r") as f:
            tasks = json.load(f)
        print("Tasks loaded successfully!")
    except FileNotFoundError:
        tasks = []  
        print("No saved tasks found, starting fresh!")

import json
# empty list to store tasks
tasks = []
load_tasks()

while True:
    print("\n----- To-Do List Manager -----")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Delete Task")
    print("4. Edit a Task")
    print("5. Marked as Completed")
    print("6. Set Priority of a Task")
    print("7. Save and Exit")

    choice = input("Enter your choice (1-7): ")

    if choice == "1":
        add_task()

    elif choice == "2":
        view_tasks()

    elif choice == "3":
        view_tasks()
        if tasks:  
            try:
                task_number = int(input("Enter task number to delete: "))
                delete_task(task_number)
            except ValueError:
                print("Please enter a valid number.")

    elif choice == "4":  
        if tasks:
            try:
                task_number = int(input("Enter task number to edit: "))
                new_task = input("Enter new task description: ")
                new_priority = input("Enter new priority (high/medium/low): ")
                edit_task(task_number, new_task, new_priority)  
            except ValueError:
                print("Please enter a valid number.")

    elif choice == "5":
        view_tasks()  
        if tasks:   
            try:
                task_number = int(input("Enter task number to mark as completed: "))
                mark_completed(task_number) 
            except ValueError:
                print("Please enter a valid number.")

    elif choice == "6":   
        view_tasks()
        if tasks:
            try:
                task_number = int(input("Enter task number to set priority: "))
                new_priority = input("Enter new priority (High/Medium/Low): ")
                set_priority(task_number, new_priority) 
            except ValueError:
                print("Please enter a valid number.")

    elif choice == "7":
        save_tasks()
        print("Saving and Exiting To-Do List Manager.")
        break

    else:
        print("Invalid choice! Please select 1-7.")
        
