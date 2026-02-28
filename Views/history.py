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
        
        self.setup_ui()
        self.refresh_data()

    def refresh_data(self):
        # Fetch all, then filter for history (Checked-out)
        data = database.get_all_reservations()
        # row_data columns: [guest_name, room_num, dates, cost, pay_status, status, id, phone, id_num, check_in, check_out, days]
        self.all_data = [list(r) for r in data if r[5] == 'Checked-out']
        self.display_data = self.all_data.copy()
        self.update_table()

    def setup_ui(self):
        container = tk.Frame(self, bg=self.COLORS["bg"], padx=30, pady=30)
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
        
        # Scrollable table container
        canvas = tk.Canvas(table_card, bg=self.COLORS["card"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=canvas.yview)
        self.table_body = tk.Frame(canvas, bg=self.COLORS["card"])
        
        self.table_body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.table_body, anchor="nw", width=1200) # Increased width
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Table Header
        header_row = tk.Frame(self.table_body, bg=self.COLORS["sidebar"], pady=15, padx=20)
        header_row.pack(fill="x")
        cols = ["Guest Name", "Room Number", "Booking Dates", "Total Payment", "Payment Status", "Status"]
        for i, col in enumerate(cols):
            lbl = tk.Label(header_row, text=col.upper(), font=("Segoe UI", 10, "bold"),
                           fg=self.COLORS["accent"], bg=self.COLORS["sidebar"])
            lbl.grid(row=0, column=i, sticky="ew")
            header_row.grid_columnconfigure(i, weight=1)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def update_table(self):
        # Clear existing rows (except header)
        for widget in self.table_body.winfo_children():
            if widget.winfo_class() != "Frame" or len(widget.winfo_children()) == 0: continue # Basic check
            # We want to keep the header_row. It was the first Frame added.
            
        # Refill
        # Actually easier to just clear all and re-add header if we want clean code
        for widget in self.table_body.winfo_children(): widget.destroy()
        
        # Re-add Header
        header_row = tk.Frame(self.table_body, bg=self.COLORS["sidebar"], pady=15, padx=20)
        header_row.pack(fill="x")
        cols = ["Guest Name", "Room Number", "Booking Dates", "Total Payment", "Payment Status", "Status"]
        for i, col in enumerate(cols):
            lbl = tk.Label(header_row, text=col.upper(), font=("Segoe UI", 10, "bold"),
                           fg=self.COLORS["accent"], bg=self.COLORS["sidebar"])
            lbl.grid(row=0, column=i, sticky="ew")
            header_row.grid_columnconfigure(i, weight=1)

        for row_data in self.display_data:
            row = tk.Frame(self.table_body, bg=self.COLORS["card"], pady=15, padx=20)
            row.pack(fill="x")
            tk.Frame(self.table_body, bg=self.COLORS["border"], height=1).pack(fill="x")

            for i, val in enumerate(row_data[:6]):
                row.grid_columnconfigure(i, weight=1)
                
                if i == 3: # Price
                    display_val = f"GH₵ {val:,.2f}"
                    tk.Label(row, text=display_val, font=("Segoe UI", 11), fg=self.COLORS["text_primary"], 
                             bg=self.COLORS["card"]).grid(row=0, column=i)
                elif i == 4: # Pay Status
                    color = self.COLORS["success"] if val == "Paid" else self.COLORS["danger"]
                    badge = tk.Frame(row, bg=color, padx=12, pady=4)
                    badge.grid(row=0, column=i)
                    tk.Label(badge, text=val.upper(), font=("Segoe UI", 8, "bold"), fg="white", bg=color).pack()
                elif i == 5: # Status
                    badge = tk.Frame(row, bg=self.COLORS["warning"], padx=12, pady=4)
                    badge.grid(row=0, column=i)
                    tk.Label(badge, text=val.upper(), font=("Segoe UI", 8, "bold"), fg="white", bg=self.COLORS["warning"]).pack()
                else:
                    tk.Label(row, text=val, font=("Segoe UI", 11), fg=self.COLORS["text_primary"], 
                             bg=self.COLORS["card"]).grid(row=0, column=i)

    def search_history(self, query):
        query = query.lower()
        if not query:
            self.display_data = self.all_data.copy()
        else:
            self.display_data = [r for r in self.all_data if any(query in str(v).lower() for v in r)]
        self.update_table()
