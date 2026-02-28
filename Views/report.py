# Report page placeholder
import tkinter as tk

class ReportPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f7f7fa")
        label = tk.Label(self, text="Report Page", font=("Arial", 18, "bold"), bg="#f7f7fa", fg="#a23bb9")
        label.pack(pady=100)
