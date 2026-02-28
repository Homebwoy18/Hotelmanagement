
# Launch the modern Login UI
import tkinter as tk
from Views.Login import LoginWindow

if __name__ == "__main__":
	root = tk.Tk()
	root.withdraw()  # Hide the root window
	login = LoginWindow(master=root)
	login.mainloop()