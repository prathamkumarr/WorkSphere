# main_app.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import requests
import threading
import json
import os

# URL where API is running
BASE_URL = "http://127.0.0.1:8000"

def run_in_thread(fn):
    """Decorator: run function in background thread."""
    def wrapper(*args, callback=None, **kwargs):
        def target():
            try:
                result = fn(*args, **kwargs)
                if callback:
                    args[0].after(1, lambda: callback(result))
            except Exception as e:
                err_msg = str(e)  # capturing exception before lambda
                if callback:
                    args[0].after(1, lambda: callback({"__error__": err_msg}))
        t = threading.Thread(target=target, daemon=True)
        t.start()
    return wrapper


class WorkSphereApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WorkSphere App")
        self.geometry("900x650")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Helvetica", 12), foreground="#111111")
        style.configure("TButton",
                relief="raised",
                background="#f0f0f0",      
                borderwidth=1,
                padding=(8, 5),
        )
        style.map("TButton",
            background=[("active", "#e5e5e5"),     
                    ("pressed", "#d9d9d9"),    
                    ("!active", "#f0f0f0"),],
                relief=[("pressed", "sunken")]
        )

        style.configure("TCombobox", font=("Helvetica", 11))
        style.configure("TNotebook.Tab", font=("Helvetica", 11, "bold"))
        style.configure("OutputFrame.TFrame", background="#e9e9e9")
        style.configure("Vertical.TScrollbar",
                background="#d6d6d6",
                troughcolor="#fafafa",
                bordercolor="#fafafa",
                arrowcolor="#333333")
        style.configure("Accent.TButton",
            font=("Helvetica", 11, "bold"),
            relief="raised",
            highlightthickness=1,
            borderwidth=1,
            padding=(10, 6)
        )
        style.map("Accent.TButton",
            background=[("active", "#e8e8e8"), ("pressed", "#d0d0d0")],
            relief=[("pressed", "sunken")]
        )

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)

        self.create_todo_tab()
        self.create_password_tab()
        self.create_rps_tab()
        self.create_employee_tab()
        self.create_files_tab()
        self.create_detective_tab()

    def create_output_box(self, parent, height=15, font=("Helvetica", 13), bg="#fafafa"):
        output_frame = ttk.Frame(parent, style="OutputFrame.TFrame")
        output_frame.pack(fill="both", expand=True, padx=14, pady=10)

        scrollbar = ttk.Scrollbar(output_frame, style="Vertical.TScrollbar")
        scrollbar.pack(side="right", fill="y")

        text_box = tk.Text(output_frame,
                        wrap="word",
                        yscrollcommand=scrollbar.set,
                        height=height,
                        font=font,
                        fg="#111111",
                        bg=bg,
                        relief="sunken",
                        bd=2,
                        padx=8, pady=6,
                        insertbackground="#111111")
        text_box.pack(fill="both", expand=True)
        scrollbar.config(command=text_box.yview)
        return text_box


    # ----------------------------
    #  To-Do Tab
    # ----------------------------
    def create_todo_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="To-Do List")

        # Responsive grid setup
        frame.grid_rowconfigure(2, weight=1) 
        frame.grid_columnconfigure(0, weight=1)

        # Task Entry + Dropdowns 
        top1 = ttk.Frame(frame)
        top1.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))
        top1.grid_columnconfigure(1, weight=1)  # Entry expands when window resizes

        ttk.Label(top1, text="Task:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.todo_entry = ttk.Entry(top1, width=40)
        self.todo_entry.grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(top1, text="Priority:").grid(row=0, column=2, sticky="w", padx=(10, 5))
        self.priority_var = tk.StringVar(value="Medium")
        ttk.Combobox(
            top1, textvariable=self.priority_var,
            values=["High", "Medium", "Low"], width=10, state="readonly"
        ).grid(row=0, column=3, padx=5)

        ttk.Label(top1, text="Status:").grid(row=0, column=4, sticky="w", padx=(10, 5))
        self.status_var = tk.StringVar(value="Pending")
        ttk.Combobox(
            top1, textvariable=self.status_var,
            values=["Pending", "Completed"], width=10, state="readonly"
        ).grid(row=0, column=5, padx=5)

        ttk.Button(top1, text="Add Task", command=self.add_task).grid(row=0, column=6, padx=(15, 5), sticky="ew")

        # Centered Action Buttons 
        top2 = ttk.Frame(frame)
        top2.grid(row=1, column=0, sticky="ew", padx=10, pady=(2, 10))
        top2.grid_columnconfigure((0, 1, 2, 3), weight=1)  # Equal spacing for buttons
 
        ttk.Button(top2, text="Edit Task", command=self.edit_task).grid(row=0, column=0, padx=8, sticky="ew")
        ttk.Button(top2, text="Delete Task", command=self.delete_task).grid(row=0, column=1, padx=8, sticky="ew")
        ttk.Button(top2, text="Mark Done", command=self.mark_complete).grid(row=0, column=2, padx=8, sticky="ew")
        ttk.Button(top2, text="Set Priority", command=self.set_priority).grid(row=0, column=3, padx=8, sticky="ew")

        # Scrollable Output Box
        output_container = ttk.Frame(frame)
        output_container.grid(row=2, column=0, sticky="nsew", padx=14, pady=(10, 14))
        self.todo_output = self.create_output_box(output_container, height=15)

        # Initial load of tasks
        self.load_tasks()

    # -----------------------  
    @run_in_thread
    def _api_get_tasks(self):
        res = requests.get(f"{BASE_URL}/todo/")
        res.raise_for_status()
        return res.json()

    def load_tasks(self):
        def cb(result):
            self.todo_output.delete("1.0", tk.END)
            if isinstance(result, dict) and "message" in result:
                self.todo_output.insert(tk.END, result["message"])
                return
            for i, t in enumerate(result, start=1):
                self.todo_output.insert(
                    tk.END,
                    f"{i}. Task: {t['task']}  |  Priority: {t['priority']}  |  Status: {'Completed' if t.get('completed') else 'Pending'}\n{'-'*70}\n\n"
                )
            self.refresh_btn.state(["disabled"])
        self._api_get_tasks(callback=cb)

    # --------------------------
    @run_in_thread
    def _api_add_task(self, task, priority, completed):
        res = requests.post(f"{BASE_URL}/todo/add", json={"task": task, "priority": priority, "completed": completed})
        res.raise_for_status()
        return res.json()

    def add_task(self):
        txt = self.todo_entry.get().strip()
        priority = self.priority_var.get()
        status = self.status_var.get() == "Completed"
        if not txt:
            messagebox.showwarning("Input", "Type a task first!")
            return
        def cb(result):
            self.todo_output.insert(tk.END, f"\n{result.get('message', str(result))}\n")
            self.todo_entry.delete(0, tk.END)
            self.refresh_btn.state(["!disabled"])  
            self.load_tasks()  # Real-time reload
        self._api_add_task(txt, priority, status, callback=cb)

    # ----------------------------
    def delete_task(self):
        task_num = simpledialog.askinteger("Delete Task", "Enter task number to delete:")
        if not task_num:
            return
        @run_in_thread
        def api_delete():
            res = requests.delete(f"{BASE_URL}/todo/delete/{task_num}")
            self.todo_output.insert(tk.END, f"\n{res.json().get('message', res.text)}\n")
            self.refresh_btn.state(["!disabled"])
            self.load_tasks()  # Reload
        api_delete()

    # -----------------------------
    def edit_task(self):
        task_num = simpledialog.askinteger("Edit Task", "Enter task number:")
        new_task = simpledialog.askstring("Edit Task", "Enter new task description(name):")
        new_priority = simpledialog.askstring("Edit Task", "Enter new priority (High/Medium/Low):")
        if not all([task_num, new_task, new_priority]):
            return
        @run_in_thread
        def api_edit():
            res = requests.put(f"{BASE_URL}/todo/edit/{task_num}?new_task={new_task}&new_priority={new_priority}")
            self.todo_output.insert(tk.END, f"\n{res.json().get('message', res.text)}\n")
            self.refresh_btn.state(["!disabled"])
            self.load_tasks()  
        api_edit()

    # -------------------------------
    def mark_complete(self):
        task_num = simpledialog.askinteger("Mark Complete", "Enter task number:")
        if not task_num:
            return
        @run_in_thread
        def api_done():
            res = requests.put(f"{BASE_URL}/todo/complete/{task_num}")
            self.todo_output.insert(tk.END, f"\n{res.json().get('message', res.text)}\n")
            self.refresh_btn.state(["!disabled"])
            self.load_tasks()
        api_done()

    # ---------------------------------
    def set_priority(self):
        task_num = simpledialog.askinteger("Set Priority", "Enter task number:")
        new_priority = simpledialog.askstring("Set Priority", "Enter new priority (High/Medium/Low):")
        if not all([task_num, new_priority]):
            return
        @run_in_thread
        def api_priority():
            res = requests.put(f"{BASE_URL}/todo/priority/{task_num}?new_priority={new_priority}")
            self.todo_output.insert(tk.END, f"\n{res.json().get('message', res.text)}\n")
            self.refresh_btn.state(["!disabled"])
            self.load_tasks()
        api_priority()


    # ----------------------------
    #  Password Tab
    # ----------------------------
    def create_password_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Password Generator")

        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        ttk.Label(frame, text="Generate a strong random password:", font=("Helvetica", 11, "bold")).grid(
            row=0, column=0, sticky="w", padx=20, pady=(15, 10)  # slightly more bottom padding
        )

        options_frame = ttk.Frame(frame)
        options_frame.grid(row=1, column=0, sticky="ew", padx=20)
        for i in range(5):
            options_frame.grid_columnconfigure(i, weight=1)

        ttk.Label(options_frame, text="Length:").grid(row=0, column=0, sticky="e", padx=(0, 5))
        self.pwd_length = ttk.Entry(options_frame, width=6)
        self.pwd_length.insert(0, "12")
        self.pwd_length.grid(row=0, column=1, sticky="w", padx=(0, 10))

        self.var_lower = tk.BooleanVar(value=True)
        self.var_upper = tk.BooleanVar(value=True)
        self.var_digits = tk.BooleanVar(value=True)
        self.var_symbols = tk.BooleanVar(value=False)
        self.var_ambiguous = tk.BooleanVar(value=True)

        ttk.Checkbutton(options_frame, text="Lowercase (a-z)", variable=self.var_lower).grid(row=0, column=2, padx=4, sticky="w")
        ttk.Checkbutton(options_frame, text="Uppercase (A-Z)", variable=self.var_upper).grid(row=0, column=3, padx=4, sticky="w")
        ttk.Checkbutton(options_frame, text="Digits (0-9)", variable=self.var_digits).grid(row=1, column=2, padx=4, sticky="w")
        ttk.Checkbutton(options_frame, text="Symbols (!@#...)", variable=self.var_symbols).grid(row=1, column=3, padx=4, sticky="w")
        ttk.Checkbutton(options_frame, text="Avoid ambiguous", variable=self.var_ambiguous).grid(
            row=0, column=4, rowspan=2, sticky="e", padx=(15, 0)
        )

        btns = ttk.Frame(frame)
        btns.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        btns.grid_columnconfigure((0, 1, 2), weight=1)

        # Centered 'Generate' initially
        self.btn_generate = ttk.Button(btns, text="Generate", command=self.generate_password)
        self.btn_generate.grid(row=0, column=1, padx=5, sticky="ew")

        # Other buttons hidden initially
        self.btn_generate_again = ttk.Button(btns, text="Generate Again", command=self.generate_again)
        self.btn_generate_again.grid(row=0, column=0, padx=5, sticky="ew")
        self.btn_generate_again.grid_remove()

        self.btn_entropy = ttk.Button(btns, text="Show Entropy Info", command=self.show_entropy)
        self.btn_entropy.grid(row=0, column=2, padx=5, sticky="ew")
        self.btn_entropy.grid_remove()
 
        # Output Box 
        output_container = ttk.Frame(frame)
        output_container.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 10))
        frame.grid_rowconfigure(3, weight=1)

        self.pwd_output = self.create_output_box(
            output_container,
            height=12,
            font=("Consolas", 15)   # monospace = cleaner alignment
        )

        # Entropy Label 
        self.entropy_label = ttk.Label(frame, text="", foreground="gray")
        self.entropy_label.grid(row=4, column=0, pady=(0, 10), sticky="w", padx=20)

    # -------------------------------
    @run_in_thread
    def _api_generate_password(self, opts=None):
        payload = opts or {
            "length": 12,
            "include_lower": True,
            "include_upper": True,
            "include_digits": True,
            "include_symbols": False,
            "avoid_ambiguous": True
        }
        res = requests.post(f"{BASE_URL}/password/generate_password", json=payload)
        res.raise_for_status()
        try:
            return res.json()
        except:
            return {"password": res.text}

    # ----------------------------------
    def generate_password(self):
        try:
            length = int(self.pwd_length.get().strip())
        except:
            messagebox.showwarning("Invalid", "Length must be an integer.")
            return

        opts = {
            "length": length,
            "include_lower": self.var_lower.get(),
            "include_upper": self.var_upper.get(),
            "include_digits": self.var_digits.get(),
            "include_symbols": self.var_symbols.get(),
            "avoid_ambiguous": self.var_ambiguous.get()
        }

        def cb(result):
            if isinstance(result, dict) and "__error__" in result:
                messagebox.showerror("Error", "Failed to generate:\n" + result["__error__"])
                return

            pwd = result.get("password", "")
            self.current_entropy = result.get("entropy_bits", None)

            # Clear output + entropy text
            self.pwd_output.delete("1.0", tk.END)
            self.entropy_label.config(text="")

            # Inserting the password
            self.pwd_output.insert(tk.END, f"Password: {pwd}")

            self.btn_generate.state(["disabled"])
            self.btn_generate.grid_remove()
            self.btn_generate_again.grid()
            self.btn_entropy.grid()

        self._api_generate_password(opts, callback=cb)

    # -----------------------------------
    def generate_again(self):
        """Always regenerates using latest UI input, not cached options"""
        # Clear output & reset UI
        self.pwd_output.delete("1.0", tk.END)
        self.entropy_label.config(text="")
        self.btn_entropy.grid_remove()

        try:
            length = int(self.pwd_length.get().strip())
        except:
            messagebox.showwarning("Invalid", "Length must be an integer.")
            return

        # Read latest checkbox states dynamically
        opts = {
            "length": length,
            "include_lower": self.var_lower.get(),
            "include_upper": self.var_upper.get(),
            "include_digits": self.var_digits.get(),
            "include_symbols": self.var_symbols.get(),
            "avoid_ambiguous": self.var_ambiguous.get()
        }

        def cb(result):
            pwd = result.get("password", "")
            self.current_entropy = result.get("entropy_bits", None)

            self.pwd_output.insert(tk.END, f"Password: {pwd}")
            self.btn_entropy.grid()

        self._api_generate_password(opts, callback=cb)

    # ----------------------------------
    def show_entropy(self):
        if hasattr(self, "current_entropy") and self.current_entropy:
            bits = self.current_entropy
            msg = f"Mathematically, your password has {bits} bits of entropy."
            if bits < 40:
                msg += " (Weak)"
            elif bits < 70:
                msg += " (Medium)"
            else:
                msg += " (Strong)"
            self.entropy_label.config(text=msg)
        else:
            self.entropy_label.config(text="Entropy not available for this password.")


    # ----------------------------
    #  Rock Paper Scissors Tab
    # ----------------------------
    def create_rps_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Rock-Paper-Scissors")

        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Game.TFrame", background="#f2f2f2")
        style.configure("Accent.TButton", background="#0078D7", foreground="white")

        ttk.Label(
            frame,
            text="Rock-Paper-Scissors - Best of Odd Rounds!",
            font=("Helvetica", 11, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))

        input_frame = ttk.Frame(frame, style="Game.TFrame")
        input_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        for i in range(3):
            input_frame.grid_columnconfigure(i, weight=1)

        # Rounds
        ttk.Label(input_frame, text="Rounds (odd):").grid(row=0, column=0, sticky="e", padx=(0, 5))
        self.rps_rounds = ttk.Entry(input_frame, width=8)
        self.rps_rounds.insert(0, "3")
        self.rps_rounds.grid(row=0, column=1, sticky="w", padx=(0, 10))

        # Moves
        ttk.Label(input_frame, text="Moves (comma sep, e.g. r,p,s) optional:").grid(
            row=1, column=0, sticky="e", padx=(0, 5), pady=(6, 0)
        )
        self.rps_moves_entry = ttk.Entry(input_frame, width=45)
        self.rps_moves_entry.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(6, 0))

        # Play Button
        self.play_btn = ttk.Button(input_frame, text="Play", command=self.play_rps)
        self.play_btn.grid(row=0, column=2, rowspan=2, sticky="ew", padx=(15, 0))

        # Separator 
        ttk.Separator(frame, orient="horizontal").grid(row=2, column=0, sticky="ew", padx=20, pady=(5, 0))

        # Game Result Text Box 
        result_container = ttk.Frame(frame)
        result_container.grid(row=3, column=0, sticky="nsew", padx=20, pady=(10, 10))
        frame.grid_rowconfigure(3, weight=1)

        self.rps_result_text = self.create_output_box(
            result_container,
            height=18,
            font=("Consolas", 13),  
            bg="#f9f9f9"                
        )

        # Play Again Button
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, pady=(5, 15))
        self.play_again_btn = ttk.Button(btn_frame, text="Play Again!", command=self.reset_rps_game)
        self.play_again_btn.pack()
        self.play_again_btn.pack_forget()

    # ---------------------------------
    @run_in_thread
    def _api_play_rps(self, rounds, moves, callback=None):
        payload = {"rounds": rounds, "moves": moves}
        print("Sending payload:", payload)

        try:
            res = requests.post(f"{BASE_URL}/rps/play_best_of", json=payload)
            print("Response code:", res.status_code)
            print("Response body:", res.text)

            if res.status_code == 200:
                try:
                    result = res.json()
                except Exception as e:
                    result = {"__error__": f"Invalid JSON: {e}\nResponse: {res.text}"}
            else:
                result = {"__error__": f"HTTP {res.status_code}: {res.text}"}

        except Exception as e:
            result = {"__error__": str(e)}

        if callback:
            self.rps_result_text.after(0, lambda: callback(result))

        return result  

    # ----------------------------------
    def play_rps(self):
        rounds_text = self.rps_rounds.get().strip()
        try:
            rounds = int(rounds_text)
        except:
            messagebox.showwarning("Invalid", "Rounds must be an integer (odd preferred).")
            return

        raw_moves = self.rps_moves_entry.get().strip()
        moves_list = []
        if raw_moves:
            cleaned = raw_moves.replace("'", "").replace('"', "").strip()
            if "," in cleaned:
                moves_list = [m.strip() for m in cleaned.split(",") if m.strip()]
            else:
                moves_list = [m.strip() for m in cleaned.split() if m.strip()]

        def cb(result):
            def update_ui():
                if not isinstance(result, dict):
                    messagebox.showerror("Error", f"Unexpected response: {result}")
                    return

                if "__error__" in result:
                    messagebox.showerror("Error", "RPS failed:\n" + result["__error__"])
                    return

                # Pretty print result
                pretty = json.dumps(result, indent=2)
                self.rps_result_text.delete("1.0", tk.END)
                self.rps_result_text.insert(tk.END, pretty)

                # Showing winner clearly
                winner = result.get("winner", None)
                if winner:
                    winner_text = "\n\nGAME OVER\n"
                    if winner.lower() == "player":
                        winner_text += "You won!"
                    elif winner.lower() == "cpu":
                        winner_text += "CPU wins! Better luck next time!"
                    else:
                        winner_text += "It's a tie!"

                    self.rps_result_text.insert(tk.END, "\n" + winner_text)

                    # Scheduling Play Again button AFTER UI is fully drawn
                    self.rps_result_text.after(
                            300,  # small delay to ensure rendering done
                            lambda: self._show_play_again() )

            # Ensure UI updates run in main thread
            self.rps_result_text.after(0, update_ui)


        # Actually trigger the API call now
        self._api_play_rps(rounds, moves_list, callback=cb)

    # ------------------------------------------------------
    def reset_rps_game(self):
        # Clear output box
        self.rps_result_text.delete("1.0", tk.END)
        self.rps_result_text.insert(tk.END, "New game started! Enter rounds and moves, then hit Play.")

        # Resetting fields
        self.rps_rounds.delete(0, tk.END)
        self.rps_rounds.insert(0, "3")
        self.rps_moves_entry.delete(0, tk.END)

        # Hide Play Again button
        self.play_again_btn.pack_forget()

    # ----------------------------------
    def _show_play_again(self):
        """Safely re-show the Play Again button"""
        self.play_again_btn.pack_forget()  # reset layout just in case
        self.play_again_btn.pack(pady=(10, 10), anchor="center")
        self.play_again_btn.update_idletasks()  # forcing Tkinter to refresh layout    


    # ----------------------------
    #  Employees Tab (basic)
    # ----------------------------
    def create_employee_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Employees Manager")

        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Title 
        ttk.Label(
            frame,
            text="Employee Management System",
            font=("Helvetica", 11, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))

        # Toolbar Buttons 
        toolbar = ttk.Frame(frame, style="Toolbar.TFrame")
        toolbar.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        for i in range(6):
            toolbar.grid_columnconfigure(i, weight=1)

        ttk.Button(toolbar, text="Add", command=self.add_employee, style="Accent.TButton").grid(row=0, column=0, padx=4, sticky="ew")
        ttk.Button(toolbar, text="Update", command=self.update_employee).grid(row=0, column=1, padx=4, sticky="ew")
        ttk.Button(toolbar, text="Delete", command=self.delete_employee).grid(row=0, column=2, padx=4, sticky="ew")
        ttk.Button(toolbar, text="Search", command=self.search_employee).grid(row=0, column=3, padx=4, sticky="ew")
        ttk.Button(toolbar, text="View All", command=self.view_employees).grid(row=0, column=4, padx=4, sticky="ew")

        # Refresh Button
        self.refresh_btn = ttk.Button(toolbar, text="Refresh", command=self.load_employees, state="disabled")
        self.refresh_btn.grid(row=0, column=5, padx=4, sticky="ew")

        # Separator
        ttk.Separator(frame, orient="horizontal").grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 5))

        # Scrollable Output Box 
        emp_container = ttk.Frame(frame)
        emp_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 10))
        frame.grid_rowconfigure(2, weight=1)

        self.emp_output = self.create_output_box(
            emp_container,
            height=20,
            font=("Consolas", 13),
            bg="#f9f9f9"
        )

        # Initial Load 
        self.load_employees()

    # -----------------------------------
    @run_in_thread
    def _api_get_employees(self):
        res = requests.get(f"{BASE_URL}/employees/")
        res.raise_for_status()
        return res.json()

    def load_employees(self):
        """Refresh employees list"""
        def cb(result):
            self.emp_output.delete("1.0", tk.END)
            if isinstance(result, dict) and "__error__" in result:
                self.emp_output.insert(tk.END, f"Failed to fetch employees:\n{result['__error__']}")
                return

            if not result:
                self.emp_output.insert(tk.END, "No employees found in the database.\n")
                return

            for e in result:
                if isinstance(e, dict):
                    text = (
                        f"ID: {e.get('id', '')}\n"
                        f"Name: {e.get('name', '')}\n"
                        f"Age: {e.get('age', '')}\n"
                        f"Department: {e.get('department', '')}\n"
                        f"Salary: Rs.{e.get('salary', '')}\n{'-'*50}\n"
                    )
                else:
                    text = f"{e}\n{'-'*50}\n"

                self.emp_output.insert(tk.END, text)

            self.refresh_btn.state(["disabled"])
        self._api_get_employees(callback=cb)

    # -----------------------------------
    def add_employee(self):
        name = simpledialog.askstring("Add Employee", "Enter employee name:")
        if not name:
            return
        age = simpledialog.askinteger("Add Employee", "Enter employee age:")
        dept = simpledialog.askstring("Add Employee", "Enter department:")
        salary = simpledialog.askfloat("Add Employee", "Enter salary:")

        if not all([name, age, dept, salary]):
            messagebox.showwarning("Missing Info", "All fields are required!")
            return

        payload = {"name": name, "age": age, "department": dept, "salary": salary}

        @run_in_thread
        def api_add():
            try:
                res = requests.post(f"{BASE_URL}/employees/add", json=payload)
                if res.status_code in (200, 201):
                    self.emp_output.insert(tk.END, f"\nEmployee Added: {name} | {dept} | Rs.{salary}\n")
                    self.refresh_btn.state(["!disabled"])
                else:
                    self.emp_output.insert(tk.END, f"\nFailed to add employee: {res.text}\n")
            except Exception as e:
                self.emp_output.insert(tk.END, f"\nError adding employee: {e}\n")

        api_add()

    # -----------------------------------
    def update_employee(self):
        emp_id = simpledialog.askinteger("Update Employee", "Enter Employee ID to update:")
        if not emp_id:
            return

        field = simpledialog.askstring("Update Employee", "Which field? (name/age/department/salary):")
        new_val = simpledialog.askstring("Update Employee", f"Enter new value for {field}:")
        if not all([field, new_val]):
            return

        @run_in_thread
        def api_update():
            try:
                res = requests.put(f"{BASE_URL}/employees/update/{emp_id}?field={field}&new_value={new_val}")
                if res.status_code == 200:
                    self.emp_output.insert(tk.END, f"\nUpdated Employee #{emp_id}: {field} → {new_val}\n")
                    self.refresh_btn.state(["!disabled"])
                else:
                    self.emp_output.insert(tk.END, f"\nFailed to update Employee #{emp_id}: {res.text}\n")
            except Exception as e:
                self.emp_output.insert(tk.END, f"\nError updating employee: {e}\n")

        api_update()

    # -----------------------------------
    def delete_employee(self):
        emp_id = simpledialog.askinteger("Delete Employee", "Enter Employee ID to delete:")
        if not emp_id:
            return

        if not messagebox.askyesno("Confirm", f"Delete employee #{emp_id}?"):
            return

        @run_in_thread
        def api_delete():
            try:
                res = requests.delete(f"{BASE_URL}/employees/delete/{emp_id}")
                if res.status_code == 200:
                    self.emp_output.insert(tk.END, f"\nEmployee #{emp_id} deleted successfully.\n")
                    self.refresh_btn.state(["!disabled"])
                else:
                    self.emp_output.insert(tk.END, f"\nFailed to delete Employee #{emp_id}: {res.text}\n")
            except Exception as e:
                self.emp_output.insert(tk.END, f"\nError deleting employee: {e}\n")

        api_delete()

    # -----------------------------------
    def search_employee(self):
        query = simpledialog.askstring("Search Employee", "Enter name or department:")
        if not query:
           return

        @run_in_thread
        def api_search():
            try:
                res = requests.get(f"{BASE_URL}/employees/search?keyword={query}")
                if res.status_code == 404:
                    self.emp_output.insert(tk.END, f"\nNo employees found for '{query}'.\n")
                    return

                result = res.json()
                self.emp_output.delete("1.0", tk.END)
                for e in result:
                    if isinstance(e, dict):
                        text = (
                            f"ID: {e.get('id', '')}\n"
                            f"Name: {e.get('name', '')}\n"
                            f"Age: {e.get('age', '')}\n"
                            f"Department: {e.get('department', '')}\n"
                            f"Salary: Rs.{e.get('salary', '')}\n{'-'*50}\n"
                        )
                    else:
                        text = f"{e}\n{'-'*50}\n"

                    self.emp_output.insert(tk.END, text)

            except Exception as e:
                self.emp_output.insert(tk.END, f"\nError searching employee: {e}\n")

        api_search()

    # -----------------------------------
    def view_employees(self):
        dept = simpledialog.askstring("View Employees", "Enter department (leave blank for all):")
        @run_in_thread
        def api_view():
            try:
                url = f"{BASE_URL}/employees/"
                if dept:
                    url += f"?department={dept}"
                res = requests.get(url)
                res.raise_for_status()
                result = res.json()
                self.emp_output.delete("1.0", tk.END)
                if not result:
                    self.emp_output.insert(tk.END, f"No employees found in '{dept}' department.\n")
                    return

                for e in result:
                    if isinstance(e, dict):
                        text = (
                            f"ID: {e.get('id', '')}\n"
                            f"Name: {e.get('name', '')}\n"
                            f"Age: {e.get('age', '')}\n"
                            f"Department: {e.get('department', '')}\n"
                            f"Salary: Rs.{e.get('salary', '')}\n{'-'*50}\n"
                        )
                    else:
                        text = f"{e}\n{'-'*50}\n"

                    self.emp_output.insert(tk.END, text)

            except Exception as e:
                self.emp_output.insert(tk.END, f"\nError viewing employees: {e}\n")

        api_view()


    # ----------------------------
    #  Files Tab (basic)
    # ----------------------------
    def create_files_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Files Manager")

        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Title
        ttk.Label(
            frame,
            text="Database File Operations",
            font=("Helvetica", 11, "bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 8))

        # Toolbar
        toolbar = ttk.Frame(frame, style="Toolbar.TFrame")
        toolbar.grid(row=1, column=0, sticky="ew", padx=20, pady=(5, 10))
        for i in range(3):
            toolbar.grid_columnconfigure(i, weight=1)

        ttk.Button(toolbar, text="Upload File", command=self.upload_file, style="Accent.TButton").grid(row=0, column=0, padx=6, sticky="ew")
        ttk.Button(toolbar, text="Export SQL : Excel", command=self.export_sql).grid(row=0, column=1, padx=6, sticky="ew")
        ttk.Button(toolbar, text="Export Mongo : CSV", command=self.export_mongo).grid(row=0, column=2, padx=6, sticky="ew")

        # Separator Line 
        ttk.Separator(frame, orient="horizontal").grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 5))

        # Scrollable Output Box
        file_container = ttk.Frame(frame)
        file_container.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 10))
        frame.grid_rowconfigure(3, weight=1)

        self.file_output = self.create_output_box(
            file_container,
            height=20,
            font=("Consolas", 13),
            bg="#f9f9f9"
        )
        self.file_output.config(cursor="arrow")

        self.file_output.insert(tk.END, "Upload or export your data from SQL/MongoDB\n\n")

    # -----------------------------------
    @run_in_thread
    def _api_upload_file(self, filepath):
        try:
            filename = os.path.basename(filepath)
            with open(filepath, "rb") as fh:
                files = {"file": (filename, fh)}
                res = requests.post(f"{BASE_URL}/files/upload", files=files)
            res.raise_for_status()
            result = res.json()
            msg = result.get("message", str(result))
            self.file_output.insert(tk.END, f"{msg}\n")
            if "rows" in result:
                self.file_output.insert(
                   tk.END,
                   f"Rows: {result['rows']} | Columns: {', '.join(result['columns'])}\n",
                )
        except Exception as e:
            self.file_output.insert(tk.END, f"Upload failed: {str(e)}\n")
        self.file_output.see(tk.END)

    def upload_file(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        self.file_output.insert(tk.END, f"Uploading '{os.path.basename(path)}'...\n")
        self._api_upload_file(path)
        self.file_output.see(tk.END)

    # -----------------------------------
    def export_sql(self):
        self.file_output.insert(tk.END, "\nExporting SQL data to Excel...\n")
        self.file_output.see(tk.END)

        @run_in_thread
        def api_export_sql():
            try:
                res = requests.get(f"{BASE_URL}/files/export/sql")
                if res.status_code == 200:
                    filename = res.headers.get("content-disposition", "file.xlsx").split("filename=")[-1]

                    # Asking where to save manually
                    save_path = filedialog.asksaveasfilename(
                        defaultextension=".xlsx",
                        initialfile=filename,
                        title="Save Exported Excel File"
                    )

                    # Save it if user chooses a location
                    if save_path:
                        with open(save_path, "wb") as f:
                            f.write(res.content)
                        self.file_output.insert(tk.END, f"Exported SQL data!\nSaved as: {save_path}\n")

                        # Creating a clickable link too 
                        self.file_output.insert(tk.END, "Open file directly: ")
                        self.file_output.insert(tk.END, "Download file!\n", ("link", save_path))
                        self.file_output.tag_config("link", foreground="blue", underline=True)
                        self.file_output.tag_bind(
                           "link",
                           "<Button-1>",
                            lambda e, path=save_path: os.startfile(path)
                            if os.name == "nt"
                            else os.system(f"open '{path}'")
                        )
                    else:
                        self.file_output.insert(tk.END, "Export canceled by user.\n")
                else:
                    self.file_output.insert(tk.END, f"Export failed: {res.text}\n")

            except Exception as e:
                self.file_output.insert(tk.END, f"Error exporting SQL: {e}\n")
            self.file_output.see(tk.END)

        api_export_sql()


    # ----------------------------------------------------------------------
    def export_mongo(self):
        self.file_output.insert(tk.END, "\nExporting MongoDB data to CSV...\n")
        self.file_output.see(tk.END)

        @run_in_thread
        def api_export_mongo():
            try:
                res = requests.get(f"{BASE_URL}/files/export/mongo")
                if res.status_code == 200:
                    filename = res.headers.get("content-disposition", "file.csv").split("filename=")[-1]

                    # Asking user where to save 
                    save_path = filedialog.asksaveasfilename(
                        defaultextension=".csv",
                        initialfile=filename,
                        title="Save Exported CSV File"
                    )

                    # Save it if user picked a location 
                    if save_path:
                        with open(save_path, "wb") as f:
                            f.write(res.content)
                        self.file_output.insert(tk.END, f"Exported MongoDB data!\nSaved as: {save_path}\n")

                        # Adding a clickable link 
                        self.file_output.insert(tk.END, "Open file directly: ")
                        self.file_output.insert(tk.END, "Download file!\n", ("link", save_path))
                        self.file_output.tag_config("link", foreground="blue", underline=True)
                        self.file_output.tag_bind(
                            "link",
                            "<Button-1>",
                            lambda e, path=save_path: os.startfile(path)
                            if os.name == "nt"
                            else os.system(f"open '{path}'")
                        )
                    else:
                        self.file_output.insert(tk.END, "Export canceled by user.\n")
                else:
                    self.file_output.insert(tk.END, f"Export failed: {res.text}\n")
            except Exception as e:
                self.file_output.insert(tk.END, f"Error exporting MongoDB: {e}\n")
            self.file_output.see(tk.END)

        api_export_mongo()


    # ----------------------------
    #  Detective Game Tab
    # ----------------------------
    def create_detective_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="Detective Game")

        # Input area
        ttk.Label(frame, text="Enter your guess:").pack(pady=(10, 5))
        self.guess_entry = ttk.Entry(frame, width=30)
        self.guess_entry.pack(pady=5)

        # Buttons frame
        btns = ttk.Frame(frame)
        btns.pack(pady=10)

        ttk.Button(btns, text="Submit Guess", command=self.submit_guess).grid(row=0, column=0, padx=6)
        ttk.Button(btns, text="Check Status", command=self.check_status).grid(row=0, column=1, padx=6)

        # Play Again button (hidden initially)
        self.reset_button = ttk.Button(btns, text="Reset Game", command=self.reset_game)
        self.reset_button.grid(row=0, column=2, padx=6)
        self.reset_button.grid_remove()

        # scrollable Output box
        detective_container = ttk.Frame(frame)
        detective_container.pack(padx=10, pady=10, fill="both", expand=True)

        self.detective_output = self.create_output_box(
            detective_container,
            height=25,
            font=("Consolas", 13),
            bg="#f9f9f9"
        )
        self.detective_output.config(relief="solid", bd=1)

    # -----------------------------
    @run_in_thread
    def _api_submit_guess(self, user_guess):
        res = requests.post(f"{BASE_URL}/detective/guess", json={"guess": user_guess})
        res.raise_for_status()
        return res.json()

    def submit_guess(self):
        user_guess = self.guess_entry.get().strip()
        if not user_guess:
            messagebox.showwarning("Input Required", "Please enter a number before guessing!")
            return

        def cb(result):
            if isinstance(result, dict) and "__error__" in result:
                messagebox.showerror("Error", "Failed to submit guess:\n" + result["__error__"])
                return

            # Show result in output box
            self.detective_output.insert(tk.END, f"Guess Result:\n{json.dumps(result, indent=2)}\n\n")

            if result.get("status") in ["Success", "Failed", "Game Over"]:
                self.reset_button.config(text="Play Again")
                self.reset_button.grid()  # show the button
            else:
                self.reset_button.grid_remove()  # hide during active gameplay

            # Clear guess input field after each attempt
            self.guess_entry.delete(0, tk.END)

        self._api_submit_guess(user_guess, callback=cb)

    # ------------------------------
    @run_in_thread
    def _api_check_status(self):
        res = requests.get(f"{BASE_URL}/detective/status")
        res.raise_for_status()
        return res.json()

    def check_status(self):
        def cb(result):
            if isinstance(result, dict) and "__error__" in result:
                messagebox.showerror("Error", "Failed to fetch status:\n" + result["__error__"])
                return
            # Extract message info
            msg = result.get("message", "")
            attempts_used = result.get("attempts_used") or (result.get("max_attempts", 15) - result.get("attempts_left", 15))
            attempts_left = result.get("attempts_left", "N/A")
            status = result.get("status", "Unknown")

            # Create a clean display
            formatted_output = f"""
            Detective Report:

            Message: {msg}
            Attempts Used: {attempts_used}
            Attempts Left: {attempts_left}
            Status: {status}
            """

            self.detective_output.insert(tk.END, formatted_output + "\n")
            self.detective_output.see(tk.END)
        self._api_check_status(callback=cb)

    # -----------------------------
    @run_in_thread
    def _api_reset_game(self):
        res = requests.post(f"{BASE_URL}/detective/reset")
        res.raise_for_status()
        return res.json()

    def reset_game(self):
        try:
            res = requests.post(f"{BASE_URL}/detective/reset")
            res.raise_for_status()
            result = res.json()

            self.detective_output.delete("1.0", tk.END)
            self.guess_entry.delete(0, tk.END)

            msg = result.get("message", "New game started!")

            self.detective_output.tag_configure("center", justify='center')
            self.detective_output.tag_add("center", "1.0", "end")

            # Hide button until next game over
            self.reset_button.grid_remove()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset game: {e}")

# -----------------------------
if __name__ == "__main__":
    app = WorkSphereApp()
    app.mainloop()
