# Booking History Page
import tkinter as tk
from tkinter import ttk
import database

class HistoryPage(tk.Frame):
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
            "warning": "#F59E0B",
            "info": "#3B82F6"
        }
        
        super().__init__(parent, bg=self.COLORS["bg"])
        self.search_var = tk.StringVar()
        self.all_data = []
        self.display_data = []
        self.table_body = None
        self.canvas_window = None # Initialize for the resize handler
        
        self.setup_ui()
        self.refresh_data()

    def refresh_data(self):
        # Fetch all, then filter for history (Checked-out)
        data = database.get_all_reservations()
        self.all_data = [list(r) for r in data if r[5] == 'Checked-out']
        self.display_data = self.all_data.copy()
        self.update_table()

    def setup_ui(self):
        # Container with standard padding to match dashboard's main area (padx=40)
        container = tk.Frame(self, bg=self.COLORS["bg"], padx=40, pady=30)
        container.pack(fill="both", expand=True)
        
        # Header
        header = tk.Frame(container, bg=self.COLORS["bg"])
        header.pack(fill="x", pady=(0, 20))
        tk.Label(header, text="Booking History Archives", font=("Segoe UI", 24, "bold"), 
                 fg=self.COLORS["text_primary"], bg=self.COLORS["bg"]).pack(side="left")
        
        # Search
        search_frame = tk.Frame(header, bg=self.COLORS["card"], padx=15, pady=8, 
                               highlightbackground=self.COLORS["border"], highlightthickness=1)
        search_frame.pack(side="right")
        tk.Label(search_frame, text="🔍", bg=self.COLORS["card"], fg=self.COLORS["text_secondary"]).pack(side="left")
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, bg=self.COLORS["card"], 
                                fg=self.COLORS["text_primary"], insertbackground="white", border=0, 
                                font=("Segoe UI", 11), width=40)
        search_entry.pack(side="left", padx=10)
        self.search_var.trace_add("write", lambda *args: self.search_history(self.search_var.get()))

        # Table Section
        table_card = tk.Frame(container, bg=self.COLORS["card"], highlightbackground=self.COLORS["border"], highlightthickness=1)
        table_card.pack(fill="both", expand=True)
        
        # Scrollable table container - Now filling the full width like dashboard
        canvas = tk.Canvas(table_card, bg=self.COLORS["card"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=canvas.yview)
        self.table_body = tk.Frame(canvas, bg=self.COLORS["card"])
        
        # Standard full-width window (no centering anchor="n")
        self.canvas_window = canvas.create_window((0, 0), window=self.table_body, anchor="nw")
        
        # Configure binding to ensure table body fills the canvas width
        def _on_canvas_configure(event):
            if self.canvas_window:
                canvas.itemconfig(self.canvas_window, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mousewheel - With Existence Check
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass 
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def update_table(self):
        for widget in self.table_body.winfo_children(): widget.destroy()
        
        # Re-add Header
        header_row = tk.Frame(self.table_body, bg=self.COLORS["sidebar"], pady=15, padx=20)
        header_row.pack(fill="x")
        cols = ["Guest Name", "Phone", "Room Number", "Booking Dates", "Total Payment", "Payment Status", "Status"]
        weights = [20, 15, 10, 20, 10, 10, 10]
        for i, col in enumerate(cols):
            lbl = tk.Label(header_row, text=col.upper(), font=("Segoe UI", 10, "bold"),
                           fg=self.COLORS["accent"], bg=self.COLORS["sidebar"])
            lbl.grid(row=0, column=i, sticky="ew")
            header_row.grid_columnconfigure(i, weight=weights[i])

        for row_data in self.display_data:
            # row_data: [guest_name, room_num, dates, cost, pay_status, status, id, phone, id_num, d1, d2, days]
            row = tk.Frame(self.table_body, bg=self.COLORS["card"], pady=12, padx=20)
            row.pack(fill="x")
            tk.Frame(self.table_body, bg=self.COLORS["border"], height=1).pack(fill="x")

            weights = [20, 15, 10, 20, 10, 10, 10]
            for i in range(len(weights)):
                row.grid_columnconfigure(i, weight=weights[i])

            # Column 0: Name
            tk.Label(row, text=row_data[0], font=("Segoe UI", 11), fg=self.COLORS["text_primary"], bg=self.COLORS["card"]).grid(row=0, column=0, sticky="ew")
            
            # Column 1: Phone
            tk.Label(row, text=row_data[7], font=("Segoe UI", 11), fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).grid(row=0, column=1, sticky="ew")

            # Column 2: Room
            tk.Label(row, text=row_data[1], font=("Segoe UI", 11), fg=self.COLORS["text_primary"], bg=self.COLORS["card"]).grid(row=0, column=2, sticky="ew")

            # Column 3: Dates
            tk.Label(row, text=row_data[2], font=("Segoe UI", 11), fg=self.COLORS["text_primary"], bg=self.COLORS["card"]).grid(row=0, column=3, sticky="ew")

            # Column 4: Total
            tk.Label(row, text=f"GH₵ {row_data[3]:,.2f}", font=("Segoe UI", 11), fg=self.COLORS["text_primary"], bg=self.COLORS["card"]).grid(row=0, column=4, sticky="ew")

            # Column 5: Payment
            p_val = row_data[4]
            p_color = self.COLORS["success"] if p_val == "Paid" else self.COLORS["danger"]
            p_badge_container = tk.Frame(row, bg=self.COLORS["card"])
            p_badge_container.grid(row=0, column=5, sticky="ew")
            p_badge = tk.Frame(p_badge_container, bg=p_color, padx=12, pady=4)
            p_badge.pack()
            tk.Label(p_badge, text=p_val.upper(), font=("Segoe UI", 8, "bold"), fg="white", bg=p_color).pack()

            # Column 6: Status
            s_badge_container = tk.Frame(row, bg=self.COLORS["card"])
            s_badge_container.grid(row=0, column=6, sticky="ew")
            s_badge = tk.Frame(s_badge_container, bg=self.COLORS["warning"], padx=12, pady=4)
            s_badge.pack()
            tk.Label(s_badge, text=row_data[5].upper(), font=("Segoe UI", 8, "bold"), fg="white", bg=self.COLORS["warning"]).pack()

    def search_history(self, query):
        query = query.lower()
        if not query:
            self.display_data = self.all_data.copy()
        else:
            self.display_data = [r for r in self.all_data if any(query in str(v).lower() for v in r)]
        self.update_table()
