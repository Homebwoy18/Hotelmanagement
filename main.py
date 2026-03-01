# Launch the modern Login UI
import tkinter as tk
from Views.Login import LoginWindow

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    # Check if a root already exists to prevent duplicates on restart
    # Actually destroying and recreating is cleaner for re-entry
    login = LoginWindow(master=root)
    login.mainloop()

if __name__ == "__main__":
    main()