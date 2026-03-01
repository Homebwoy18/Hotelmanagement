# Sales History Page
import tkinter as tk
from tkinter import ttk, messagebox
import database

class SalesHistoryPage(tk.Frame):
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
        self.all_sales = []
        self.display_sales = []
        
        # Pagination
        self.current_page = 0
        self.rows_per_page = 12
        self.weights = [10, 25, 10, 15, 15, 15, 10]
        self.cols = ["ID", "ITEM NAME", "QTY", "TOTAL", "METHOD", "DATE", "ROOM"]
        
        self.search_var = tk.StringVar()
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        container = tk.Frame(self, bg=self.COLORS["bg"], padx=40, pady=30)
        container.pack(fill="both", expand=True)

        # 1. Header & Stats
        header = tk.Frame(container, bg=self.COLORS["bg"])
        header.pack(fill="x", pady=(0, 30))
        
        tk.Label(header, text="📈 Sales History", font=("Segoe UI", 24, "bold"), 
                 fg=self.COLORS["text_primary"], bg=self.COLORS["bg"]).pack(side="left")

        # Stats Cards Row
        stats_row = tk.Frame(container, bg=self.COLORS["bg"])
        stats_row.pack(fill="x", pady=(0, 40))
        
        self.daily_sales_card = self.create_stat_card(stats_row, "Daily Sales Count", "0", self.COLORS["success"])
        self.daily_sales_card.pack(side="left", padx=(0, 20), expand=True, fill="both")
        
        self.total_rev_card = self.create_stat_card(stats_row, "Daily Revenue", "GH₵ 0.00", self.COLORS["accent"])
        self.total_rev_card.pack(side="left", padx=(0, 20), expand=True, fill="both")
        
        # 2. Search & Table Title
        table_controls = tk.Frame(container, bg=self.COLORS["bg"])
        table_controls.pack(fill="x", pady=(0, 15))
        
        tk.Label(table_controls, text="📜 All Transactions", font=("Segoe UI", 18, "bold"), 
                 fg=self.COLORS["accent"], bg=self.COLORS["bg"]).pack(side="left")
        
        search_frame = tk.Frame(table_controls, bg=self.COLORS["card"], padx=10, pady=5,
                               highlightbackground=self.COLORS["border"], highlightthickness=1)
        search_frame.pack(side="right")
        tk.Label(search_frame, text="🔍", bg=self.COLORS["card"], fg=self.COLORS["text_secondary"]).pack(side="left")
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, bg=self.COLORS["card"], 
                                fg=self.COLORS["text_primary"], border=0, font=("Segoe UI", 11), width=40)
        search_entry.pack(side="left", padx=10)
        self.search_var.trace_add("write", lambda *args: self.search_data())

        # 3. Table Structure
        log_card = tk.Frame(container, bg=self.COLORS["card"], highlightbackground=self.COLORS["border"], highlightthickness=1)
        log_card.pack(fill="both", expand=True)

        # Header
        self.table_header = tk.Frame(log_card, bg=self.COLORS["sidebar"], pady=15, padx=25)
        self.table_header.pack(fill="x")
        for i, text in enumerate(self.cols):
            tk.Label(self.table_header, text=text, font=("Segoe UI", 9, "bold"), 
                     bg=self.COLORS["sidebar"], fg=self.COLORS["accent"]).grid(row=0, column=i, sticky="ew")
            self.table_header.grid_columnconfigure(i, weight=self.weights[i])

        # Body
        self.table_body = tk.Frame(log_card, bg=self.COLORS["card"])
        self.table_body.pack(fill="both", expand=True)

        # Pagination Footer
        self.pagination_frame = tk.Frame(container, bg=self.COLORS["bg"], pady=20)
        self.pagination_frame.pack(fill="x")

    def create_stat_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=self.COLORS["card"], padx=25, pady=25,
                       highlightbackground=self.COLORS["border"], highlightthickness=1)
        tk.Label(card, text=title, font=("Segoe UI", 12), fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).pack(anchor="w")
        val_lbl = tk.Label(card, text=value, font=("Segoe UI", 24, "bold"), fg=color, bg=self.COLORS["card"])
        val_lbl.pack(anchor="w", pady=(10, 0))
        card.value_label = val_lbl
        return card

    def refresh_data(self):
        # Update Stats
        stats = database.get_daily_sales_stats()
        self.daily_sales_card.value_label.config(text=str(stats['daily_count']))
        self.total_rev_card.value_label.config(text=f"GH₵ {stats['daily_revenue']:,.2f}")
        
        # Load Sales
        self.all_sales = database.get_sales_report()
        self.display_sales = list(self.all_sales)
        self.update_table()

    def search_data(self):
        query = self.search_var.get().lower().strip()
        if not query:
            self.display_sales = list(self.all_sales)
        else:
            self.display_sales = [s for s in self.all_sales if 
                                 query in str(s['id']).lower() or 
                                 query in s['name'].lower() or 
                                 query in s['payment_method'].lower() or 
                                 (s['room_number'] and query in str(s['room_number']).lower())]
        self.current_page = 0
        self.update_table()

    def update_table(self):
        for widget in self.table_body.winfo_children(): widget.destroy()

        total_items = len(self.display_sales)
        total_pages = max(1, (total_items + self.rows_per_page - 1) // self.rows_per_page)
        
        if self.current_page >= total_pages: self.current_page = total_pages - 1
        start = self.current_page * self.rows_per_page
        end = start + self.rows_per_page
        page_data = self.display_sales[start:end]

        for s in page_data:
            r = tk.Frame(self.table_body, bg=self.COLORS["card"], pady=15, padx=25)
            r.pack(fill="x")
            date_str = s['sale_date'].split('.')[0] if s['sale_date'] else "N/A"
            data = [s['id'], s['name'], s['quantity'], f"GH₵ {s['total_cost']:,.2f}", s['payment_method'], date_str, s['room_number'] or "-"]
            
            for i, val in enumerate(data):
                r.grid_columnconfigure(i, weight=self.weights[i])
                tk.Label(r, text=val, font=("Segoe UI", 10), bg=self.COLORS["card"], 
                         fg="white" if i != 3 else self.COLORS["success"], 
                         anchor="center" if i > 1 else "w").grid(row=0, column=i, sticky="ew")
            tk.Frame(self.table_body, bg=self.COLORS["border"], height=1).pack(fill="x")

        self.update_pagination_controls(total_pages)

    def update_pagination_controls(self, total_pages):
        for widget in self.pagination_frame.winfo_children(): widget.destroy()
        inner_p = tk.Frame(self.pagination_frame, bg=self.COLORS["bg"])
        inner_p.pack()

        tk.Button(inner_p, text="←", font=("Segoe UI", 10, "bold"),
                  fg="white" if self.current_page > 0 else self.COLORS["text_secondary"],
                  bg=self.COLORS["sidebar"] if self.current_page > 0 else self.COLORS["bg"],
                  bd=0, padx=15, pady=8, cursor="hand2" if self.current_page > 0 else "arrow",
                  command=self.prev_page).pack(side="left", padx=5)

        tk.Label(inner_p, text=f"Page {self.current_page + 1} of {total_pages}",
                 font=("Segoe UI", 11), fg=self.COLORS["text_primary"], bg=self.COLORS["bg"]).pack(side="left", padx=20)

        tk.Button(inner_p, text="→", font=("Segoe UI", 10, "bold"),
                  fg="white" if self.current_page < total_pages - 1 else self.COLORS["text_secondary"],
                  bg=self.COLORS["sidebar"] if self.current_page < total_pages - 1 else self.COLORS["bg"],
                  bd=0, padx=15, pady=8, cursor="hand2" if self.current_page < total_pages - 1 else "arrow",
                  command=self.next_page).pack(side="left", padx=5)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_table()

    def next_page(self):
        total_items = len(self.display_sales)
        total_pages = (total_items + self.rows_per_page - 1) // self.rows_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_table()
