import subprocess
import time
import os
import logging
import socket

# Path to Anaconda Python interpreter
PYTHON_PATH = "/opt/anaconda3/bin/python3"

# Setting up log file on Desktop 
log_file = os.path.expanduser("~/Desktop/WorkSphere_log.txt")
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")
logging.info("WorkSphere app started.")

# directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define script paths
main_py = os.path.join(BASE_DIR, "main.py")          # FastAPI backend file
main_app_py = os.path.join(BASE_DIR, "main_app.py")  # Tkinter frontend file

# Function to check if a port is open
def wait_for_port(host, port, timeout=20):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            try:
                s.connect((host, port))
                return True
            except (ConnectionRefusedError, OSError):
                time.sleep(0.5)
    return False

# Starting backend server
print("Starting backend server...")
logging.info("Starting backend server...")

try:
    backend = subprocess.Popen(
        [PYTHON_PATH, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=BASE_DIR
    )

    # Wait for backend port to open
    print("Waiting for backend to become ready...")
    if wait_for_port("127.0.0.1", 8000):
        print("Backend is ready!")
        logging.info("Backend is ready!")
    else:
        print("Backend failed to start within timeout.")
        logging.error("Backend failed to start within timeout.")
        backend.terminate()
        exit(1)

    # Launching Tkinter frontend
    print("Launching frontend UI...")
    logging.info("Launching frontend UI...")
    os.system(f'"{PYTHON_PATH}" "{main_app_py}"')

finally:
    print("Shutting down backend...")
    logging.info("Shutting down backend...")
    backend.terminate()
