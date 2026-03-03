# Booking History Page
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import database
from Views.theme import COLORS

class HistoryPage(tk.Frame):
    def __init__(self, parent):
        self.COLORS = COLORS
        
        super().__init__(parent, bg=self.COLORS["bg"])
        self.search_var = tk.StringVar()
        self.all_data = []
        self.display_data = []
        self.table_body = None
        self.canvas_window = None 
        
        # Pagination
        self.current_page = 0
        self.rows_per_page = 10
        self.weights = [20, 15, 12, 22, 12, 10, 10]
        self.cols = ["Guest Name", "Phone", "Room", "Booking Dates", "Payment", "Pay Stat", "Status"]
        self.pagination_frame = None
        
        self.setup_ui()
        self.refresh_data()
        
        # Unbind mousewheel when destroyed
        self.bind("<Destroy>", self.on_destroy)

    def on_destroy(self, event):
        if event.widget == self:

            try:
                self.unbind_all("<MouseWheel>")
            except: pass

    def setup_ui(self):
        # Container with standard padding to match dashboard's main area (padx=40)
        container = tk.Frame(self, bg=self.COLORS["bg"], padx=40, pady=30)
        container.pack(fill="both", expand=True)
        
        # Header
        header = tk.Frame(container, bg=COLORS["bg"])
        header.pack(fill="x", pady=(0, 20))
        tk.Label(header, text="Booking History Archives", font=("Segoe UI", 24, "bold"),
                 fg=COLORS["text_primary"], bg=COLORS["bg"]).pack(side="left")

        # CSV Export button
        tk.Button(header, text="⬇ Export CSV", font=("Segoe UI", 10, "bold"),
                  fg="white", bg=COLORS["success"], activebackground="#059669",
                  activeforeground="white", bd=0, padx=14, pady=6, cursor="hand2",
                  command=self.export_csv).pack(side="right", padx=(0, 10))
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

        # Structural fix for exact column alignment: Header and Canvas share inner_container
        # Scrollbar is outside inner_container
        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=None) # Command set later
        scrollbar.pack(side="right", fill="y")
        
        inner_container = tk.Frame(table_card, bg=self.COLORS["card"])
        inner_container.pack(side="left", fill="both", expand=True)

        # Table Header (Inside inner_container)
        self.header_frame = tk.Frame(inner_container, bg=self.COLORS["sidebar"], pady=15, padx=20)
        self.header_frame.pack(fill="x")
        for i, col in enumerate(self.cols):
            tk.Label(self.header_frame, text=col.upper(), font=("Segoe UI", 10, "bold"),
                     fg=self.COLORS["accent"], bg=self.COLORS["sidebar"]).grid(row=0, column=i, sticky="ew")
            self.header_frame.grid_columnconfigure(i, weight=self.weights[i])

        # Canvas (Inside inner_container)
        canvas = tk.Canvas(inner_container, bg=self.COLORS["card"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        scrollbar.config(command=canvas.yview)

        self.table_body = tk.Frame(canvas, bg=self.COLORS["card"])
        self.canvas_window = canvas.create_window((0, 0), window=self.table_body, anchor="nw")
        
        def _on_canvas_configure(event):
            if self.canvas_window:
                canvas.itemconfig(self.canvas_window, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pagination Controls
        self.pagination_frame = tk.Frame(container, bg=self.COLORS["bg"], pady=20)
        self.pagination_frame.pack(fill="x")
        
        # Mousewheel - With Existence Check
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except:
                pass 
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def refresh_data(self):
        # Fetch all, then filter for history (Checked-out)
        data = database.get_all_reservations()
        self.all_data = [list(r) for r in data if r[5] == 'Checked-out']
        self.display_data = self.all_data.copy()
        self.current_page = 0 # Reset to first page on refresh
        self.update_table()

    def update_table(self):
        if not self.table_body: return
        for widget in self.table_body.winfo_children(): widget.destroy()
        
        # 1. Pagination Slice
        total_items = len(self.display_data)
        total_pages = max(1, (total_items + self.rows_per_page - 1) // self.rows_per_page)
        
        if self.current_page >= total_pages: self.current_page = total_pages - 1
        start = self.current_page * self.rows_per_page
        end = start + self.rows_per_page
        page_data = self.display_data[start:end]

        # 2. Render Page Rows
        for row_data in page_data:
            # row_data: [guest_name, room_num, dates, cost, pay_status, status, id, phone, id_num, d1, d2, days]
            row = tk.Frame(self.table_body, bg=self.COLORS["card"], pady=12, padx=20)
            row.pack(fill="x")
            
            for i in range(len(self.weights)):
                row.grid_columnconfigure(i, weight=self.weights[i])

            # Column 0: Name
            tk.Label(row, text=row_data[0][:25], font=("Segoe UI", 11), fg=self.COLORS["text_primary"], 
                     bg=self.COLORS["card"], anchor="w").grid(row=0, column=0, sticky="ew")
            
            # Column 1: Phone
            tk.Label(row, text=row_data[7], font=("Segoe UI", 11), fg=self.COLORS["text_secondary"], 
                     bg=self.COLORS["card"], anchor="w").grid(row=0, column=1, sticky="ew")

            # Column 2: Room
            tk.Label(row, text=row_data[1], font=("Segoe UI", 11), fg=self.COLORS["text_primary"], 
                     bg=self.COLORS["card"], anchor="center").grid(row=0, column=2, sticky="ew")

            # Column 3: Dates
            tk.Label(row, text=row_data[2], font=("Segoe UI", 10), fg=self.COLORS["text_primary"], 
                     bg=self.COLORS["card"], anchor="w").grid(row=0, column=3, sticky="ew")

            # Column 4: Total Cost
            tk.Label(row, text=f"GH₵ {row_data[3]:,.2f}", font=("Segoe UI", 11, "bold"), 
                     fg=self.COLORS["text_primary"], bg=self.COLORS["card"], anchor="e").grid(row=0, column=4, sticky="ew", padx=(0, 10))

            # Column 5: Payment Status Badge
            p_val = row_data[4]
            p_color = self.COLORS["success"] if p_val == "Paid" else self.COLORS["danger"]
            p_badge_container = tk.Frame(row, bg=self.COLORS["card"])
            p_badge_container.grid(row=0, column=5, sticky="ew")
            p_badge = tk.Frame(p_badge_container, bg=p_color, padx=10, pady=4)
            p_badge.pack()
            tk.Label(p_badge, text=p_val.upper(), font=("Segoe UI", 8, "bold"), fg="white", bg=p_color).pack()

            # Column 6: Status Badge
            s_badge_container = tk.Frame(row, bg=self.COLORS["card"])
            s_badge_container.grid(row=0, column=6, sticky="ew")
            s_badge = tk.Frame(s_badge_container, bg=self.COLORS["warning"], padx=10, pady=4)
            s_badge.pack()
            tk.Label(s_badge, text=row_data[5].upper(), font=("Segoe UI", 8, "bold"), fg="white", bg=self.COLORS["warning"]).pack()

            tk.Frame(self.table_body, bg=self.COLORS["border"], height=1).pack(fill="x")

        # 3. Render Pagination Controls
        self.update_pagination_controls(total_pages)

    def update_pagination_controls(self, total_pages):
        for widget in self.pagination_frame.winfo_children(): widget.destroy()
        
        # Center the buttons
        inner_p = tk.Frame(self.pagination_frame, bg=self.COLORS["bg"])
        inner_p.pack()

        prev_btn = tk.Button(inner_p, text="← Previous", font=("Segoe UI", 10, "bold"),
                            fg="white" if self.current_page > 0 else self.COLORS["text_secondary"],
                            bg=self.COLORS["sidebar"] if self.current_page > 0 else self.COLORS["bg"],
                            bd=0, padx=15, pady=8, cursor="hand2" if self.current_page > 0 else "arrow",
                            command=self.prev_page)
        prev_btn.pack(side="left", padx=10)

        page_lbl = tk.Label(inner_p, text=f"Page {self.current_page + 1} of {total_pages}",
                           font=("Segoe UI", 11), fg=self.COLORS["text_primary"], bg=self.COLORS["bg"])
        page_lbl.pack(side="left", padx=20)

        next_btn = tk.Button(inner_p, text="Next →", font=("Segoe UI", 10, "bold"),
                            fg="white" if self.current_page < total_pages - 1 else self.COLORS["text_secondary"],
                            bg=self.COLORS["sidebar"] if self.current_page < total_pages - 1 else self.COLORS["bg"],
                            bd=0, padx=15, pady=8, cursor="hand2" if self.current_page < total_pages - 1 else "arrow",
                            command=self.next_page)
        next_btn.pack(side="left", padx=10)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_table()

    def next_page(self):
        total_items = len(self.display_data)
        total_pages = (total_items + self.rows_per_page - 1) // self.rows_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_table()

    def search_history(self, query):
        query = query.lower()
        if not query:
            self.display_data = self.all_data.copy()
        else:
            self.display_data = [r for r in self.all_data if any(query in str(v).lower() for v in r)]
        self.update_table()

    def export_csv(self):
        if not self.display_data:
            messagebox.showinfo("Export", "No data to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Booking History",
            initialfile="booking_history.csv"
        )
        if not path:
            return
        headers = ["Guest Name", "Room", "Stay Period", "Total Cost", "Pay Status",
                   "Status", "ID", "Phone", "ID Number", "Check-in", "Check-out", "Days"]
        try:
            import csv
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(self.display_data)
            messagebox.showinfo("Export Successful", f"Data saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
