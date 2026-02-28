
# Redesigned Professional Rooms Page
import tkinter as tk
from tkinter import ttk

class RoomsPage(tk.Frame):
    def __init__(self, parent):
        self.COLORS = {
            "bg": "#111827",
            "sidebar": "#1F2937",
            "card": "#1F2937",
            "accent": "#6366F1",
            "text_primary": "#F9FAFB",
            "text_secondary": "#9CA3AF",
            "border": "#374151",
            "success": "#10B981",
            "danger": "#EF4444",
            "warning": "#F59E0B"
        }
        super().__init__(parent, bg=self.COLORS["bg"])
        
        self.rooms_list_frame = None
        self.create_widgets()

    def create_widgets(self):
        # Header with Search/Actions
        header_frame = tk.Frame(self, bg=self.COLORS["bg"])
        header_frame.pack(fill="x", pady=(10, 30))

        # Search Box (Modern style)
        search_container = tk.Frame(header_frame, bg=self.COLORS["card"], 
                                    padx=15, pady=8, highlightbackground=self.COLORS["border"], highlightthickness=1)
        search_container.pack(side="left")
        
        tk.Label(search_container, text="🔍", bg=self.COLORS["card"], fg=self.COLORS["text_secondary"]).pack(side="left")
        search_entry = tk.Entry(search_container, bg=self.COLORS["card"], fg=self.COLORS["text_primary"], 
                                 insertbackground="white", border=0, font=("Segoe UI", 11), width=30)
        search_entry.pack(side="left", padx=10)
        search_entry.insert(0, "Search rooms...")

        # Add Room Button (Simulated Rounded)
        add_btn_container = tk.Frame(header_frame, bg=self.COLORS["accent"], padx=20, pady=10)
        add_btn_container.pack(side="right")
        add_btn = tk.Label(add_btn_container, text="+ Add New Room", font=("Segoe UI", 11, "bold"),
                           fg="white", bg=self.COLORS["accent"], cursor="hand2")
        add_btn.pack()

        # Rooms List Container (Card Style)
        main_container = tk.Frame(self, bg=self.COLORS["card"], 
                                 highlightbackground=self.COLORS["border"], highlightthickness=1)
        main_container.pack(fill="both", expand=True)

        # Table Header
        header_cols = ["Room Number", "Type", "Status", "Price", "Actions"]
        table_header = tk.Frame(main_container, bg=self.COLORS["sidebar"], pady=15)
        table_header.pack(fill="x")
        
        for i, col in enumerate(header_cols):
            lbl = tk.Label(table_header, text=col.upper(), font=("Segoe UI", 10, "bold"),
                           fg=self.COLORS["accent"], bg=self.COLORS["sidebar"])
            lbl.grid(row=0, column=i, sticky="ew")
            table_header.grid_columnconfigure(i, weight=1)

        # Content Area with Scroll (Simple implementation for now)
        self.rooms_list_frame = tk.Frame(main_container, bg=self.COLORS["card"])
        self.rooms_list_frame.pack(fill="both", expand=True)

        # Example data
        rooms_data = [
            ("101", "Single Deluxe", "Available", "$120"),
            ("102", "Double Suite", "Occupied", "$250"),
            ("103", "Grand Suite", "Maintenance", "$450"),
            ("104", "Single Basic", "Available", "$80"),
            ("105", "Double Deluxe", "Available", "$180"),
            ("106", "Single Deluxe", "Occupied", "$120"),
        ]

        for idx, (num, r_type, status, price) in enumerate(rooms_data):
            row = tk.Frame(self.rooms_list_frame, bg=self.COLORS["card"], pady=12)
            row.pack(fill="x")
            
            # Row border bottom
            sep = tk.Frame(self.rooms_list_frame, bg=self.COLORS["border"], height=1)
            sep.pack(fill="x")

            # Shared style for row labels
            label_style = {"bg": self.COLORS["card"], "fg": self.COLORS["text_primary"], "font": ("Segoe UI", 11)}

            # Column frames for alignment
            for i in range(5):
                row.grid_columnconfigure(i, weight=1)

            # Col 1: Room Num
            tk.Label(row, text=num, font=("Segoe UI", 11, "bold"), fg=self.COLORS["text_primary"], bg=self.COLORS["card"]).grid(row=0, column=0)
            
            # Col 2: Type
            tk.Label(row, text=r_type, **label_style).grid(row=0, column=1)
            
            # Col 3: Status Badge
            status_color = self.COLORS["success"] if status == "Available" else (self.COLORS["danger"] if status == "Occupied" else self.COLORS["warning"])
            badge_bg = tk.Frame(row, bg=status_color, padx=12, pady=4)
            badge_bg.grid(row=0, column=2)
            tk.Label(badge_bg, text=status.upper(), font=("Segoe UI", 9, "bold"), fg="white", bg=status_color).pack()

            # Col 4: Price
            tk.Label(row, text=price, font=("Segoe UI", 11, "bold"), fg=self.COLORS["accent"], bg=self.COLORS["card"]).grid(row=0, column=3)

            # Col 5: Actions
            actions_frame = tk.Frame(row, bg=self.COLORS["card"])
            actions_frame.grid(row=0, column=4)
            tk.Label(actions_frame, text="Edit", fg=self.COLORS["accent"], bg=self.COLORS["card"], 
                     font=("Segoe UI", 10, "underline"), cursor="hand2").pack(side="left", padx=5)
            tk.Label(actions_frame, text="Delete", fg=self.COLORS["danger"], bg=self.COLORS["card"], 
                     font=("Segoe UI", 10, "underline"), cursor="hand2").pack(side="left", padx=5)
