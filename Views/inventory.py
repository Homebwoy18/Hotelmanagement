# Inventory page placeholder
import tkinter as tk

class InventoryPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f7f7fa")
        # Title
        title = tk.Label(self, text="Inventory", font=("Segoe UI", 22, "bold"), bg="#f7f7fa", fg="#5b2d91")
        title.pack(anchor="w", padx=40, pady=(28, 10))

        # Table container
        table_frame = tk.Frame(self, bg="#f7f7fa", bd=0, highlightbackground="#e5e5ef", highlightthickness=1)
        table_frame.pack(fill="x", padx=40, pady=(0, 28))

        # Table header
        headers = ["Item", "Quantity", "Status", "Location"]
        for idx, header in enumerate(headers):
            tk.Label(table_frame, text=header, font=("Segoe UI", 11, "bold"), bg="#f7f7fa", fg="#5b2d91").grid(row=0, column=idx, padx=10, pady=10)

        # Example data
        data = [
            ("Towels", "120", "In Stock", "Store Room 1"),
            ("Bedsheets", "60", "Low Stock", "Store Room 2"),
            ("Soap", "200", "In Stock", "Store Room 1"),
            ("Shampoo", "30", "Low Stock", "Store Room 2"),
        ]
        for row_idx, row in enumerate(data, start=1):
            for col_idx, value in enumerate(row):
                tk.Label(table_frame, text=value, font=("Segoe UI", 11), bg="#f7f7fa", fg="#222").grid(row=row_idx, column=col_idx, padx=10, pady=8)
