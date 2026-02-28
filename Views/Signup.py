# Modern Signup UI in Tkinter
import tkinter as tk
from tkinter import messagebox

class SignupWindow(tk.Toplevel):
	def __init__(self, master=None):
		super().__init__(master)
		self.title("Sign Up - Hotel Management")
		self.geometry("1000x650")
		self.configure(bg="#181f2a")
		self.resizable(True, True)
		self.state('zoomed')  # Start maximized
		self.create_widgets()

	def create_widgets(self):
		# Top-right navigation button to Login
		# Main container frame (centered)
		container = tk.Frame(self, bg="#181f2a")
		container.pack(expand=True, fill="both")




		# Use a grid for left and right panels
		container.columnconfigure(0, weight=1, minsize=500)
		container.columnconfigure(1, weight=1, minsize=500)
		container.rowconfigure(0, weight=1)

		# Navigation link (top right, floating)
		# (No login button at top, as requested)
		left_frame = tk.Frame(container, bg="#181f2a")
		left_frame.grid(row=0, column=0, sticky="nsew", padx=(60, 30), pady=60)
		left_frame.grid_propagate(False)
		left_frame.update_idletasks()
		left_frame_height = left_frame.winfo_reqheight()
		# Add a spacer frame to push content down
		spacer = tk.Frame(left_frame, bg="#181f2a", height=80)
		spacer.pack()

		logo = tk.Label(left_frame, text="HotelEase", font=("Arial Black", 32, "bold"), fg="white", bg="#181f2a")
		logo.pack(anchor="w", pady=(0, 20))

		welcome = tk.Label(left_frame, text="Join HotelEase!", font=("Arial", 30, "bold"), fg="white", bg="#181f2a")
		welcome.pack(anchor="w", pady=(0, 10))

		desc = tk.Label(left_frame, text="Create your account to book rooms,\nmanage reservations, and enjoy exclusive hotel offers!",
				font=("Arial", 11), fg="#b0b8c1", bg="#181f2a", justify="left")
		desc.pack(anchor="w", pady=(0, 30))



		# Right side (Sign Up)
		right_frame = tk.Frame(container, bg="#232b39")
		right_frame.grid(row=0, column=1, sticky="nsew", padx=(30, 60), pady=60)
		right_frame.configure(highlightbackground="#232b39", highlightthickness=2)

		# Center the form in right_frame
		form = tk.Frame(right_frame, bg="#232b39")
		form.pack(expand=True)

		signup_label = tk.Label(form, text="HotelEase Signup", font=("Arial", 22, "bold"), fg="white", bg="#232b39")
		signup_label.grid(row=0, column=0, columnspan=2, pady=(10, 25))

		user_label = tk.Label(form, text="Username", font=("Arial", 12, "bold"), fg="#b0b8c1", bg="#232b39", anchor="w")
		user_label.grid(row=1, column=0, sticky="w", padx=(10, 0), pady=(0, 8))
		self.username_entry = tk.Entry(form, font=("Arial", 12), bg="#3a4252", fg="white", bd=0, relief="flat", insertbackground="white", width=28)
		self.username_entry.grid(row=1, column=1, pady=(0, 8), ipady=7, padx=(0, 10))

		email_label = tk.Label(form, text="Email", font=("Arial", 12, "bold"), fg="#b0b8c1", bg="#232b39", anchor="w")
		email_label.grid(row=2, column=0, sticky="w", padx=(10, 0), pady=(0, 8))
		self.email_entry = tk.Entry(form, font=("Arial", 12), bg="#3a4252", fg="white", bd=0, relief="flat", insertbackground="white", width=28)
		self.email_entry.grid(row=2, column=1, pady=(0, 8), ipady=7, padx=(0, 10))

		pass_label = tk.Label(form, text="Password", font=("Arial", 12, "bold"), fg="#b0b8c1", bg="#232b39", anchor="w")
		pass_label.grid(row=3, column=0, sticky="w", padx=(10, 0), pady=(0, 8))
		self.password_entry = tk.Entry(form, font=("Arial", 12), bg="#3a4252", fg="white", bd=0, relief="flat", show="*", insertbackground="white", width=28)
		self.password_entry.grid(row=3, column=1, pady=(0, 8), ipady=7, padx=(0, 10))

		confirm_label = tk.Label(form, text="Confirm Password", font=("Arial", 12, "bold"), fg="#b0b8c1", bg="#232b39", anchor="w")
		confirm_label.grid(row=4, column=0, sticky="w", padx=(10, 0), pady=(0, 18))
		self.confirm_entry = tk.Entry(form, font=("Arial", 12), bg="#3a4252", fg="white", bd=0, relief="flat", show="*", insertbackground="white", width=28)
		self.confirm_entry.grid(row=4, column=1, pady=(0, 18), ipady=7, padx=(0, 10))

		submit_btn = tk.Button(form, text="Create Account", font=("Arial", 14, "bold"), fg="white", bg="#ff512f",
							  activebackground="#dd2476", activeforeground="white", bd=0, relief="flat", padx=10, pady=8,
							  command=self.submit)
		submit_btn.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 18))

		or_label = tk.Label(form, text="Or", font=("Arial", 12), fg="#b0b8c1", bg="#232b39")
		or_label.grid(row=6, column=0, columnspan=2, pady=(0, 10))

		# Social icons (using emoji as placeholders)
		social_frame = tk.Frame(form, bg="#232b39")
		social_frame.grid(row=7, column=0, columnspan=2, pady=(0, 10))
		for icon in ["\U0001F426", "\U0001F4F7", "\U0001F4F1"]:  # Twitter, Instagram, Facebook
			tk.Label(social_frame, text=icon, font=("Arial", 18), bg="#232b39", fg="#b0b8c1").pack(side="left", padx=10)

		login_frame = tk.Frame(form, bg="#232b39")
		login_frame.grid(row=8, column=0, columnspan=2, pady=(10, 0))
		login_label = tk.Label(login_frame, text="Already have a HotelEase account? ", font=("Arial", 11), fg="#b0b8c1", bg="#232b39")
		login_label.pack(side="left")
		login_btn = tk.Button(login_frame, text="Login", font=("Arial", 11, "bold"), fg="#ff512f", bg="#232b39", bd=0, relief="flat", cursor="hand2", command=self.open_login)
		login_btn.pack(side="left")

	def submit(self):
		username = self.username_entry.get()
		email = self.email_entry.get()
		password = self.password_entry.get()
		confirm = self.confirm_entry.get()
		# Placeholder for signup logic
		if not username or not email or not password or not confirm:
			messagebox.showerror("Error", "All fields are required.")
		elif password != confirm:
			messagebox.showerror("Error", "Passwords do not match.")
		else:
			messagebox.showinfo("Success", "Account created successfully!")

	def open_login(self):
		self.destroy()
		from Views.Login import LoginWindow
		LoginWindow(self.master)


if __name__ == "__main__":
	root = tk.Tk()
	root.withdraw()  # Hide the root window
	signup = SignupWindow(master=root)
	signup.mainloop()
