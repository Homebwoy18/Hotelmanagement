import tkinter as tk
from tkinter import messagebox
import database
from Views.theme import COLORS, HOTEL_NAME

class SignupWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title(f"Sign Up - {HOTEL_NAME} Management")
        self.geometry("1000x700")
        self.configure(bg=COLORS["bg"])
        self.resizable(True, True)
        self.state('zoomed')
        self.username_entry = None
        self.email_entry = None
        self.password_entry = None
        self.confirm_entry = None
        self._show_password = False
        self._show_confirm = False
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

        spacer = tk.Frame(left_frame, bg=COLORS["bg"], height=80)
        spacer.pack()

        tk.Label(left_frame, text=HOTEL_NAME, font=("Arial Black", 32, "bold"),
                 fg=COLORS["accent"], bg=COLORS["bg"]).pack(anchor="w", pady=(0, 20))

        tk.Label(left_frame, text=f"Join {HOTEL_NAME}!",
                 font=("Arial", 30, "bold"), fg="white", bg=COLORS["bg"]).pack(anchor="w", pady=(0, 10))

        tk.Label(left_frame,
                 text="Create your account to book rooms,\nmanage reservations, and enjoy exclusive hotel offers!",
                 font=("Arial", 11), fg=COLORS["text_secondary"], bg=COLORS["bg"], justify="left").pack(anchor="w", pady=(0, 30))

        # ── Right panel (form) ────────────────────────────────────────
        right_frame = tk.Frame(container, bg=COLORS["card"])
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(30, 60), pady=60)
        right_frame.configure(highlightbackground=COLORS["border"], highlightthickness=1)

        form = tk.Frame(right_frame, bg=COLORS["card"])
        form.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(form, text=f"{HOTEL_NAME} – Sign Up", font=("Arial", 20, "bold"),
                 fg="white", bg=COLORS["card"]).pack(pady=(0, 15))

        # ── Helper ──
        def field(label_text, show=None, err_name=None):
            tk.Label(form, text=label_text, font=("Arial", 11, "bold"),
                     fg=COLORS["text_secondary"], bg=COLORS["card"], anchor="w").pack(fill="x")
            row_frame = tk.Frame(form, bg="#3a4252")
            row_frame.pack(fill="x", pady=(2, 0))
            e = tk.Entry(row_frame, font=("Arial", 11), bg="#3a4252", fg="white",
                         bd=0, relief="flat", insertbackground="white",
                         show=show if show else "")
            e.pack(side="left", fill="both", expand=True, ipady=7, padx=(4, 0))
            toggle = None
            if show == "*":
                state = {"visible": False}
                def make_toggle(entry, st):
                    def _tog():
                        st["visible"] = not st["visible"]
                        entry.config(show="" if st["visible"] else "*")
                    return _tog
                toggle = tk.Button(row_frame, text="👁", font=("Arial", 10),
                                   bg="#3a4252", fg=COLORS["text_secondary"], bd=0,
                                   cursor="hand2", activebackground="#3a4252",
                                   command=make_toggle(e, state))
                toggle.pack(side="right", padx=(0, 6))
            err = tk.Label(form, text="", font=("Arial", 9), fg=COLORS["danger"],
                           bg=COLORS["card"], anchor="w")
            err.pack(fill="x", pady=(1, 6))
            if err_name:
                setattr(self, err_name, err)
            return e

        self.username_entry = field("Username", err_name="user_err")
        self.email_entry    = field("Email", err_name="email_err")
        self.password_entry = field("Password", show="*", err_name="pass_err")
        self.confirm_entry  = field("Confirm Password", show="*", err_name="conf_err")

        # Password strength bar
        self.strength_lbl = tk.Label(form, text="", font=("Arial", 9),
                                     fg=COLORS["text_secondary"], bg=COLORS["card"], anchor="w")
        self.strength_lbl.pack(fill="x", pady=(0, 8))
        self.password_entry.bind("<KeyRelease>", self._check_strength)

        # Bind Enter on confirm field
        self.confirm_entry.bind("<Return>", lambda e: self.submit())

        # Submit
        submit_btn = tk.Button(form, text="Create Account", font=("Arial", 13, "bold"),
                               fg="white", bg="#ff512f", activebackground=COLORS["accent"],
                               activeforeground="white", bd=0, relief="flat", padx=10, pady=9,
                               cursor="hand2", command=self.submit)
        submit_btn.pack(fill="x", pady=(2, 12))
        submit_btn.bind("<Enter>", lambda e: submit_btn.config(bg=COLORS["accent"]))
        submit_btn.bind("<Leave>", lambda e: submit_btn.config(bg="#ff512f"))

        login_frame = tk.Frame(form, bg=COLORS["card"])
        login_frame.pack()
        tk.Label(login_frame, text=f"Already have a {HOTEL_NAME} account? ",
                 font=("Arial", 10), fg=COLORS["text_secondary"], bg=COLORS["card"]).pack(side="left")
        tk.Button(login_frame, text="Login", font=("Arial", 10, "bold"),
                  fg="#ff512f", bg=COLORS["card"], bd=0, relief="flat",
                  cursor="hand2", activeforeground=COLORS["accent"],
                  activebackground=COLORS["card"], command=self.open_login).pack(side="left")

        self.after(100, lambda: self.username_entry.focus_set())

    def _check_strength(self, event=None):
        pw = self.password_entry.get()
        score = 0
        if len(pw) >= 8:   score += 1
        if len(pw) >= 12:  score += 1
        if any(c.isupper() for c in pw): score += 1
        if any(c.isdigit() for c in pw): score += 1
        if any(c in "!@#$%^&*()_-+=[]{}|;:',.<>?/`~" for c in pw): score += 1
        labels = ["", "⬛ Very Weak", "🟥 Weak", "🟧 Fair", "🟨 Good", "🟩 Strong"]
        self.strength_lbl.config(text=labels[min(score, 5)] if pw else "")

    def _clear_errors(self):
        for attr in ("user_err", "email_err", "pass_err", "conf_err"):
            if hasattr(self, attr):
                getattr(self, attr).config(text="")

    def submit(self):
        self._clear_errors()
        username = self.username_entry.get().strip()
        email    = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm  = self.confirm_entry.get()

        valid = True
        if not username:
            self.user_err.config(text="⚠ Username is required.")
            valid = False
        if not email or "@" not in email:
            self.email_err.config(text="⚠ Enter a valid email address.")
            valid = False
        if not password:
            self.pass_err.config(text="⚠ Password is required.")
            valid = False
        elif len(password) < 6:
            self.pass_err.config(text="⚠ Password must be at least 6 characters.")
            valid = False
        if password and confirm != password:
            self.conf_err.config(text="⚠ Passwords do not match.")
            valid = False
        if not valid:
            return

        success, msg = database.add_user(username, email, password)
        if success:
            messagebox.showinfo("Account Created", msg)
            self.open_login()
        else:
            self.user_err.config(text=f"⚠ {msg}")

    def open_login(self):
        self.destroy()
        from Views.Login import LoginWindow
        LoginWindow(self.master)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    signup = SignupWindow(master=root)
    signup.mainloop()
