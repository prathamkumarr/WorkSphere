# employee management system
import sqlite3

# estaiblishing connection with DB
conn = sqlite3.connect("employees.db")
cursor = conn.cursor()

# creating table structure in database
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    department TEXT,
    salary INTEGER
)
""")

conn.commit()

# CRUD operations
def add_employee(name, age, department, salary):
    try:
        cursor.execute("INSERT INTO employees (name, age, department, salary) VALUES (?, ?, ?, ?)", 
                    (name, age, department, salary))
        conn.commit()
        print("employee added successfully!")
    except Exception as e:
        print("Error:", e)

def view_employees(department=None):
    try:
        if department:
            cursor.execute("SELECT * FROM employees WHERE department = ?", (department,))
        else:
            cursor.execute("SELECT * FROM employees")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}, Dept: {row[3]}, Salary: {row[4]}")
        else:
            print("no employees found!")
    except Exception as e:
        print("Error:", e)

def update_employee(emp_id, field, new_value):
    try:
        allowed_fields = ["name", "age", "department", "salary"]
        if field not in allowed_fields:
            print("invalid field!")
            return
        
        cursor.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
        if not cursor.fetchone():  
            print("No employee found with this ID")
            return
        
        if field in ["age", "salary"]:
            new_value = int(new_value)

        cursor.execute(f"UPDATE employees SET {field} = ? WHERE id = ?", (new_value, emp_id))
        conn.commit()
        print("employee updated successfully!")

    except Exception as e:
        print("Error:", e)

def delete_employee(emp_id):
    try:
        cursor.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
        conn.commit()
        print("employee deleted successfully!")
    except Exception as e:
        print("Error:", e)

def search_employee(keyword):
    try:
        cursor.execute("SELECT * FROM employees WHERE LOWER(name) LIKE LOWER(?) OR LOWER(department) LIKE LOWER(?)", 
                   ('%' + keyword + '%', '%' + keyword + '%'))
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}, Dept: {row[3]}, Salary: {row[4]}")
        else:
            print("No match found!")
    except Exception as e:
        print("Error:", e)

while True:
    print("\n--- Employee Management System ---")
    print("1. Add Employee")
    print("2. View Employee")
    print("3. Update Employee")
    print("4. Delete Employee")
    print("5. Search Employee")
    print("6. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        name = input("Enter name: ")
        age = int(input("Enter age: "))
        department = input("Enter department: ")
        salary = int(input("Enter salary: "))
        add_employee(name, age, department, salary)

    elif choice == "2":
        view_employees()

    elif choice == "3":
        emp_id = int(input("Enter employee ID to update: "))
        field = input("Enter field to update (name/age/department/salary): ")
        new_value = input("Enter new value: ")
        update_employee(emp_id, field, new_value)

    elif choice == "4":
        emp_id = int(input("Enter employee ID to delete: "))
        delete_employee(emp_id)

    elif choice == "5":
        keyword = input("Enter name or department to search: ")
        search_employee(keyword)

    elif choice == "6":
        break
    else:
        print("incorrect choice, choose again.")

conn.close()


