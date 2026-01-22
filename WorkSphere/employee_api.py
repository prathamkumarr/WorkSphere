from fastapi import HTTPException, Query
from pydantic import BaseModel
import sqlite3
from fastapi import APIRouter

router = APIRouter()

# database connection setup
def get_db():
    conn = sqlite3.connect("employees.db")
    conn.row_factory = sqlite3.Row  
    return conn

# create table if not exists
with get_db() as conn:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        department TEXT,
        salary INTEGER
    )
    """)
    conn.commit()

# pydantic model for employee
class Employee(BaseModel):
    name: str
    age: int
    department: str
    salary: int

@router.get("/welcome", tags=["Employee Manager"])
def home():
    return {"message": "Welcome to Employee Manager API"}

# endpoint to add employee
@router.post("/add", tags=["Employee Manager"])
def add_employee(emp: Employee):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employees (name, age, department, salary) VALUES (?, ?, ?, ?)",
            (emp.name, emp.age, emp.department, emp.salary)
        )
        conn.commit()
        return {"message": f"Employee '{emp.name}' added successfully!"}

# endpoint to view employees
@router.get("/", tags=["Employee Manager"])
def view_employees(department: str | None = Query(None)):
    with get_db() as conn:
        cursor = conn.cursor()
        if department:
            cursor.execute("SELECT * FROM employees WHERE department = ?", (department,))
        else:
            cursor.execute("SELECT * FROM employees")
        rows = cursor.fetchall()
        if not rows:
            return {"message": "No employees found."}
        return [dict(row) for row in rows]

# endpoint to update employee
@router.put("/update/{emp_id}", tags=["Employee Manager"])
def update_employee(emp_id: int, field: str, new_value: str):
    allowed_fields = ["name", "age", "department", "salary"]
    if field not in allowed_fields:
        raise HTTPException(status_code=400, detail="Invalid field!")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Employee not found")

        if field in ["age", "salary"]:
            new_value = int(new_value)

        cursor.execute(f"UPDATE employees SET {field} = ? WHERE id = ?", (new_value, emp_id))
        conn.commit()
        return {"message": f"Employee #{emp_id} updated successfully!"}

# endpoint to delete employee
@router.delete("/delete/{emp_id}", tags=["Employee Manager"])
def delete_employee(emp_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Employee not found")
        conn.commit()
        return {"message": f"Employee #{emp_id} deleted successfully!"}

# endpoint to search employees
@router.get("/search", tags=["Employee Manager"])
def search_employee(keyword: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM employees 
        WHERE LOWER(name) LIKE LOWER(?) OR LOWER(department) LIKE LOWER(?) 
        """, ('%' + keyword + '%', '%' + keyword + '%'))
        rows = cursor.fetchall()
        if not rows:
            return {"message": f"No employees found for '{keyword}'."}
        return [dict(row) for row in rows]

