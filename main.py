from fastapi import FastAPI
from WorkSphere import file_manager_api, employee_api, todo_api, detective_api, pwd_api, rps_api

app = FastAPI(
    title="WorkSphere Unified API",
    description="All APIs merged into one FastAPI app.",
    version="1.0",
)

# Attaching routers from each file
app.include_router(file_manager_api.router, prefix="/files", tags=["File Manager"])
app.include_router(employee_api.router, prefix="/employees", tags=["Employee Manager"])
app.include_router(todo_api.router, prefix="/todo", tags=["To-Do List Manager"])
app.include_router(detective_api.router, prefix="/detective", tags=["Detective Game"])
app.include_router(pwd_api.router, prefix="/password", tags=["Password Generator"])
app.include_router(rps_api.router, prefix="/rps", tags=["Rock-Paper-Scissors"])

@app.get("/", tags=["Overview"])
def root():
    return {
        "project": "WorkSphere Unified API",
        "modules": [
            "/files",
            "/employees",
            "/todo",
            "/detective",
            "/password",
            "/rps"
        ]
    }
