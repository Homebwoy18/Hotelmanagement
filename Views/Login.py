import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import database
from Views.theme import COLORS, HOTEL_NAME, LOGO_PNG, LOGO_ICO

class LoginWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title(f"Sign In - {HOTEL_NAME} Management")
        self.geometry("1000x650")
        self.configure(bg=COLORS["bg"])
        self.resizable(True, True)
        self.state('zoomed')
        # Set window icon
        try:
            self.iconbitmap(LOGO_ICO)
        except Exception:
            pass
        self.username_entry = None
        self.password_entry = None
        self._show_password = False
        self._logo_img = None  # keep reference to prevent GC
        self.create_widgets()

    def create_widgets(self):
        container = tk.Frame(self, bg=COLORS["bg"])
        container.pack(expand=True, fill="both")

        container.columnconfigure(0, weight=1, minsize=500)
        container.columnconfigure(1, weight=1, minsize=500)
        container.rowconfigure(0, weight=1)

        # ── Left panel ──────────────────────────────────────────────
        left_frame = tk.Frame(container, bg=COLORS["bg"])
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(60, 30), pady=60)
        left_frame.grid_propagate(False)

        spacer = tk.Frame(left_frame, bg=COLORS["bg"], height=30)
        spacer.pack()

        # Hotel logo image
        try:
            raw = Image.open(LOGO_PNG).convert("RGBA")
            raw = raw.resize((180, 180), Image.LANCZOS)
            self._logo_img = ImageTk.PhotoImage(raw)
            tk.Label(left_frame, image=self._logo_img, bg=COLORS["bg"]).pack(anchor="w", pady=(0, 16))
        except Exception:
            pass

        tk.Label(left_frame, text=HOTEL_NAME, font=("Arial Black", 32, "bold"),
                 fg=COLORS["accent"], bg=COLORS["bg"]).pack(anchor="w", pady=(0, 12))

        tk.Label(left_frame, text=f"Welcome to {HOTEL_NAME}!",
                 font=("Arial", 22, "bold"), fg="white", bg=COLORS["bg"]).pack(anchor="w", pady=(0, 10))

        tk.Label(left_frame,
                 text="Your comfort is our priority.\nBook, relax, and enjoy the best hotel experience.\nSign in to manage your reservations or explore our services!",
                 font=("Arial", 11), fg=COLORS["text_secondary"], bg=COLORS["bg"], justify="left").pack(anchor="w", pady=(0, 30))

        # ── Right panel (form) ────────────────────────────────────────
        right_frame = tk.Frame(container, bg=COLORS["card"])
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(30, 60), pady=60)
        right_frame.configure(highlightbackground=COLORS["border"], highlightthickness=1)

        form = tk.Frame(right_frame, bg=COLORS["card"])
        form.pack(expand=True)

        tk.Label(form, text="Hotel Login", font=("Arial", 22, "bold"),
                 fg="white", bg=COLORS["card"]).grid(row=0, column=0, columnspan=2, pady=(10, 25))

        # Username
        tk.Label(form, text="Username", font=("Arial", 12, "bold"),
                 fg=COLORS["text_secondary"], bg=COLORS["card"], anchor="w").grid(row=1, column=0, sticky="w", padx=(10, 0), pady=(0, 4))
        self.username_entry = tk.Entry(form, font=("Arial", 12), bg="#3a4252", fg="white",
                                       bd=0, relief="flat", insertbackground="white", width=28)
        self.username_entry.grid(row=2, column=0, columnspan=2, pady=(0, 4), ipady=7, padx=10, sticky="ew")

        # Username error label
        self.user_err = tk.Label(form, text="", font=("Arial", 9), fg=COLORS["danger"],
                                  bg=COLORS["card"], anchor="w")
        self.user_err.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 4))

        # Password
        tk.Label(form, text="Password", font=("Arial", 12, "bold"),
                 fg=COLORS["text_secondary"], bg=COLORS["card"], anchor="w").grid(row=4, column=0, sticky="w", padx=(10, 0), pady=(0, 4))

        pass_frame = tk.Frame(form, bg="#3a4252")
        pass_frame.grid(row=5, column=0, columnspan=2, pady=(0, 4), padx=10, sticky="ew")

        self.password_entry = tk.Entry(pass_frame, font=("Arial", 12), bg="#3a4252", fg="white",
                                        bd=0, relief="flat", show="*", insertbackground="white")
        self.password_entry.pack(side="left", fill="both", expand=True, ipady=7, padx=(4, 0))
        self.password_entry.bind("<Return>", lambda e: self.submit())

        toggle_btn = tk.Button(pass_frame, text="👁", font=("Arial", 10), bg="#3a4252",
                               fg=COLORS["text_secondary"], bd=0, cursor="hand2",
                               activebackground="#3a4252", command=self._toggle_password)
        toggle_btn.pack(side="right", padx=(0, 6))

        # Password error label
        self.pass_err = tk.Label(form, text="", font=("Arial", 9), fg=COLORS["danger"],
                                  bg=COLORS["card"], anchor="w")
        self.pass_err.grid(row=6, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 8))

        # Submit button
        submit_btn = tk.Button(form, text="Login", font=("Arial", 14, "bold"),
                               fg="white", bg="#ff512f", activebackground=COLORS["accent"],
                               activeforeground="white", bd=0, relief="flat", padx=10, pady=8,
                               cursor="hand2", command=self.submit)
        submit_btn.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 18))
        submit_btn.bind("<Enter>", lambda e: submit_btn.config(bg=COLORS["accent"]))
        submit_btn.bind("<Leave>", lambda e: submit_btn.config(bg="#ff512f"))

        or_label = tk.Label(form, text="— or —", font=("Arial", 11), fg=COLORS["text_secondary"], bg=COLORS["card"])
        or_label.grid(row=8, column=0, columnspan=2, pady=(0, 10))

        signup_frame = tk.Frame(form, bg=COLORS["card"])
        signup_frame.grid(row=9, column=0, columnspan=2, pady=(0, 10))
        tk.Label(signup_frame, text=f"Don't have a {HOTEL_NAME} account? ",
                 font=("Arial", 11), fg=COLORS["text_secondary"], bg=COLORS["card"]).pack(side="left")
        signup_btn = tk.Button(signup_frame, text="Sign Up", font=("Arial", 11, "bold"),
                               fg="#ff512f", bg=COLORS["card"], bd=0, relief="flat",
                               cursor="hand2", activeforeground=COLORS["accent"],
                               activebackground=COLORS["card"], command=self.open_signup)
        signup_btn.pack(side="left")

        # Focus username on open
        self.after(100, lambda: self.username_entry.focus_set())

    def _toggle_password(self):
        self._show_password = not self._show_password
        self.password_entry.config(show="" if self._show_password else "*")

    def submit(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        # Clear previous inline errors
        self.user_err.config(text="")
        self.pass_err.config(text="")

        valid = True
        if not username:
            self.user_err.config(text="⚠ Username is required.")
            valid = False
        if not password:
            self.pass_err.config(text="⚠ Password is required.")
            valid = False
        if not valid:
            return

        if database.verify_user(username, password):
            self.destroy()
            self.master.deiconify()
            from Views.dashboard import DashboardWindow
            DashboardWindow(self.master)
        else:
            self.pass_err.config(text="⚠ Invalid username or password.")

    def open_signup(self):
        self.destroy()
        from Views.Signup import SignupWindow
        SignupWindow(self.master)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    login = LoginWindow(master=root)
    login.mainloop()
