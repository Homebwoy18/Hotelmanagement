# Modern Reservation Page
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import database

class ReservationPage(tk.Frame):
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
        
        # Initialize attributes
        self.entries = {}
        self.submit_btn = None
        self.search_entry = None
        self.search_var = tk.StringVar()
        self.table_body = None
        self.editing_id = None 
        self.canvas = None
        self.scrollbar = None
        self.scrollable_frame = None
        self.available_rooms = []
        self.ROOM_PRICES = {}
        self.all_data = [] 
        self.display_data = []
        
        # Load data
        self.refresh_room_data()
        self.refresh_table_data()
        
        super().__init__(parent, bg=self.COLORS["bg"])
        self.setup_ui()
        
        # Unbind mousewheel when destroyed to prevent TclError
        self.bind("<Destroy>", self.on_destroy)

    def on_destroy(self, event):
        if event.widget == self:
            try:
                self.unbind_all("<MouseWheel>")
            except: pass

    def refresh_room_data(self):
        self.ROOM_PRICES = {r['room_number']: r['price'] for r in database.get_rooms()}
        self.available_rooms = [r['room_number'] for r in database.get_rooms() if r['status'] == 'Available']

    def refresh_table_data(self):
        self.all_data = database.get_all_reservations()
        self.display_data = [list(r) for r in self.all_data]

    def setup_ui(self):
        # 1. Main Canvas for Scrolling
        self.canvas = tk.Canvas(self, bg=self.COLORS["bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.COLORS["bg"])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Mousewheel support
        def _on_mousewheel(event):
            try:
                if self.canvas and self.canvas.winfo_exists():
                    self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except: pass
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Layout Container
        main_layout = tk.Frame(self.scrollable_frame, bg=self.COLORS["bg"], padx=20, pady=20)
        main_layout.pack(fill="both", expand=True)
        
        # Header
        header = tk.Frame(main_layout, bg=self.COLORS["bg"], pady=10)
        header.pack(fill="x")
        tk.Label(header, text="Booking Management", font=("Segoe UI", 24, "bold"), 
                 fg=self.COLORS["text_primary"], bg=self.COLORS["bg"]).pack(side="left")

        # --- Horizontal Form (Top Section) ---
        tk.Label(main_layout, text="➕ Create New Booking", font=("Segoe UI", 16, "bold"), 
                 fg=self.COLORS["accent"], bg=self.COLORS["bg"]).pack(anchor="w", pady=(30, 15))

        form_card = tk.Frame(main_layout, bg=self.COLORS["card"], padx=25, pady=25,
                             highlightbackground=self.COLORS["border"], highlightthickness=1)
        form_card.pack(fill="x", pady=(0, 40))

        form_grid = tk.Frame(form_card, bg=self.COLORS["card"])
        form_grid.pack(fill="x")
        
        fields = [
            ("Customer Name", 0, 0), ("Phone Number", 0, 1),
            ("ID Number", 1, 0), ("Room", 1, 1),
            ("Check-in Date", 2, 0), ("Check-out Date", 2, 1),
            ("Number of Days", 3, 0), ("Total Cost", 3, 1),
            ("Payment Status", 4, 0)
        ]

        for i in range(4): form_grid.columnconfigure(i, weight=1)

        for name, r, c in fields:
            base_col = c * 2
            lbl = tk.Label(form_grid, text=name, font=("Segoe UI", 10), 
                           fg=self.COLORS["text_secondary"], bg=self.COLORS["card"], anchor="w")
            lbl.grid(row=r, column=base_col, sticky="w", padx=(10, 5), pady=10)
            
            if name == "Room":
                entry = ttk.Combobox(form_grid, values=self.available_rooms, font=("Segoe UI", 11), state="readonly")
                if self.available_rooms: entry.current(0)
                entry.bind("<<ComboboxSelected>>", self.calculate_cost)
            elif name in ["Check-in Date", "Check-out Date"]:
                entry = DateEntry(form_grid, font=("Segoe UI", 11), background=self.COLORS["accent"], 
                                  foreground="white", borderwidth=2)
                entry.bind("<<DateEntrySelected>>", self.calculate_cost)
            elif name == "Number of Days":
                days_list = [str(i) for i in range(1, 31)]
                entry = ttk.Combobox(form_grid, values=days_list, font=("Segoe UI", 11), state="readonly")
                entry.current(0)
                entry.bind("<<ComboboxSelected>>", self.recalculate_from_days)
            elif name == "Payment Status":
                entry = ttk.Combobox(form_grid, values=["Paid", "Unpaid"], font=("Segoe UI", 11), state="readonly")
                entry.current(1)
            else:
                entry = tk.Entry(form_grid, font=("Segoe UI", 11), bg="#374151", fg="white", 
                                 insertbackground="white", border=0)
                if name == "Total Cost":
                    entry.config(state="readonly", readonlybackground="white", fg="black")
            
            entry.grid(row=r, column=base_col+1, sticky="ew", padx=(0, 10), pady=10, ipady=5)
            self.entries[name] = entry

        self.submit_btn = tk.Button(form_card, text="Add Reservation", font=("Segoe UI", 12, "bold"),
                                   fg="white", bg=self.COLORS["accent"], activebackground="#4F46E5",
                                   activeforeground="white", bd=0, relief="flat", pady=10, cursor="hand2",
                                   command=self.save_reservation)
        self.submit_btn.pack(side="right", padx=10, pady=(20, 0), ipadx=30)
        
        self.calculate_cost()

        # --- Table Section ---
        table_header_section = tk.Frame(main_layout, bg=self.COLORS["bg"])
        table_header_section.pack(fill="x", pady=(20, 15))
        tk.Label(table_header_section, text="🔍 Booking History", font=("Segoe UI", 16, "bold"), 
                 fg=self.COLORS["accent"], bg=self.COLORS["bg"]).pack(side="left")

        search_container = tk.Frame(table_header_section, bg=self.COLORS["card"], 
                                    padx=15, pady=8, highlightbackground=self.COLORS["border"], highlightthickness=1)
        search_container.pack(side="right")
        tk.Label(search_container, text="🔍", bg=self.COLORS["card"], fg=self.COLORS["text_secondary"]).pack(side="left")
        self.search_entry = tk.Entry(search_container, textvariable=self.search_var, bg=self.COLORS["card"], 
                                     fg=self.COLORS["text_primary"], insertbackground="white", border=0, 
                                     font=("Segoe UI", 11), width=40)
        self.search_entry.pack(side="left", padx=10)
        self.search_var.trace_add("write", lambda *args: self.search_bookings(self.search_var.get()))

        table_card = tk.Frame(main_layout, bg=self.COLORS["card"], 
                              highlightbackground=self.COLORS["border"], highlightthickness=1)
        table_card.pack(fill="x", pady=(0, 40))
        
        table_cols = tk.Frame(table_card, bg=self.COLORS["sidebar"], pady=15, padx=20)
        table_cols.pack(fill="x")
        cols = ["Guest Name", "Room", "Dates", "Total", "Payment", "Status", "Actions"]
        for i, col in enumerate(cols):
            lbl = tk.Label(table_cols, text=col.upper(), font=("Segoe UI", 10, "bold"),
                           fg=self.COLORS["accent"], bg=self.COLORS["sidebar"])
            lbl.grid(row=0, column=i, sticky="ew")
            table_cols.grid_columnconfigure(i, weight=1)

        self.table_body = tk.Frame(table_card, bg=self.COLORS["card"])
        self.table_body.pack(fill="both", expand=True)

        self.update_table()

    def update_table(self):
        if not self.table_body: return
        for widget in self.table_body.winfo_children():
            widget.destroy()

        for idx, row_data in enumerate(self.display_data):
            # row_data columns: [guest_name, room_num, dates, cost, pay_status, status, id, phone, id_num, d1, d2, days]
            row = tk.Frame(self.table_body, bg=self.COLORS["card"], pady=15, padx=20)
            row.pack(fill="x")
            tk.Frame(self.table_body, bg=self.COLORS["border"], height=1).pack(fill="x")

            for i, val in enumerate(row_data[:6]): # Show only first 6 columns
                row.grid_columnconfigure(i, weight=1)
                
                if i == 3: # Price Display
                    display_val = str(val).replace('$', 'GH₵ ').replace('GH₵ GH₵', 'GH₵')
                    tk.Label(row, text=display_val, font=("Segoe UI", 11), fg=self.COLORS["text_primary"], 
                             bg=self.COLORS["card"]).grid(row=0, column=i)
                elif i == 4: # Payment Badge
                    color = self.COLORS["success"] if val == "Paid" else self.COLORS["danger"]
                    badge = tk.Frame(row, bg=color, padx=12, pady=4)
                    badge.grid(row=0, column=i)
                    tk.Label(badge, text=val.upper(), font=("Segoe UI", 8, "bold"), fg="white", bg=color).pack()
                elif i == 5: # Status Badge
                    if val == "Confirmed": color = self.COLORS["info"]
                    elif val == "Checked-out": color = self.COLORS["warning"]
                    else: color = self.COLORS["success"]
                    
                    badge = tk.Frame(row, bg=color, padx=12, pady=4)
                    badge.grid(row=0, column=i)
                    tk.Label(badge, text=val.upper(), font=("Segoe UI", 8, "bold"), fg="white", bg=color).pack()
                else:
                    tk.Label(row, text=val, font=("Segoe UI", 11), fg=self.COLORS["text_primary"], 
                             bg=self.COLORS["card"]).grid(row=0, column=i)

            row.grid_columnconfigure(6, weight=1)
            actions = tk.Frame(row, bg=self.COLORS["card"])
            actions.grid(row=0, column=6)
            
            if row_data[5] != "Checked-out":
                tk.Button(actions, text="Checkout", font=("Segoe UI", 9, "bold"), bg=self.COLORS["danger"], 
                          fg="white", bd=0, padx=10, pady=4, cursor="hand2", 
                          command=lambda r=row_data: self.checkout_record(r)).pack(side="left", padx=5)
                
                tk.Button(actions, text="✏", font=("Segoe UI", 12), bg=self.COLORS["card"], fg=self.COLORS["accent"], bd=0, 
                          cursor="hand2", command=lambda r=row_data: self.edit_record(r)).pack(side="left", padx=5)
            else:
                tk.Label(actions, text="Archived", font=("Segoe UI", 10, "italic"), fg=self.COLORS["text_secondary"], 
                         bg=self.COLORS["card"]).pack()

    def calculate_cost(self, event=None):
        try:
            d1 = self.entries["Check-in Date"].get_date()
            d2 = self.entries["Check-out Date"].get_date()
            delta = (d2 - d1).days
            if delta < 0: delta = 0
            
            self.entries["Number of Days"].set(str(delta))
            
            room = self.entries["Room"].get()
            raw_price = self.ROOM_PRICES.get(room, "GH₵ 100")
            price_str = str(raw_price).replace('GH₵', '').replace('$', '').replace(',', '').strip()
            price = float(price_str) if price_str else 100
            total = delta * price
            
            cost_entry = self.entries["Total Cost"]
            cost_entry.config(state="normal")
            cost_entry.delete(0, tk.END)
            cost_entry.insert(0, f"GH₵ {total:,.2f}")
            cost_entry.config(state="readonly")
        except: pass

    def recalculate_from_days(self, event=None):
        try:
            days = int(self.entries["Number of Days"].get())
            d1 = self.entries["Check-in Date"].get_date()
            d2 = d1 + timedelta(days=days)
            self.entries["Check-out Date"].set_date(d2)
            self.calculate_cost()
        except: pass

    def save_reservation(self):
        self.calculate_cost()
        
        name = self.entries["Customer Name"].get()
        room = self.entries["Room"].get()
        if not name or not room:
            messagebox.showwarning("Warning", "Customer name and Room are required.")
            return

        d1 = self.entries["Check-in Date"].get_date().strftime("%Y-%m-%d")
        d2 = self.entries["Check-out Date"].get_date().strftime("%Y-%m-%d")
        cost_str = self.entries["Total Cost"].get()
        pay = self.entries["Payment Status"].get()
        phone = self.entries["Phone Number"].get() or "N/A"
        id_num = self.entries["ID Number"].get() or ""
        days = int(self.entries["Number of Days"].get() or 0)
        
        try:
            clean_cost = float(cost_str.replace('GH₵', '').replace('$', '').replace(',', '').strip())
        except:
            clean_cost = 0.0

        if database.add_reservation(name, phone, id_num, room, d1, d2, days, clean_cost, pay, res_id=self.editing_id):
            messagebox.showinfo("Success", "Reservation updated!" if self.editing_id else "Booking confirmed!")
            self.refresh_room_data()
            self.refresh_table_data()
            self.clear_form()
            self.update_table()
        else:
            messagebox.showerror("Error", "Could not save reservation.")

    def checkout_record(self, row_data):
        res_id = row_data[6]
        if messagebox.askyesno("Checkout", f"Proceed with checkout for {row_data[0]} (Room {row_data[1]})?"):
            if database.checkout_reservation(res_id):
                self.refresh_room_data()
                self.refresh_table_data()
                self.update_table()
                messagebox.showinfo("Checkout", f"Guest {row_data[0]} checked out. Room {row_data[1]} is now Available.")
            else:
                messagebox.showerror("Error", "Checkout failed.")

    def edit_record(self, row_data):
        # row_data mapping: [name, room, dates, cost, pay, status, id, phone, id_num, check_in, check_out, days]
        self.editing_id = row_data[6]
        self.submit_btn.config(text="Update Booking", bg=self.COLORS["success"])
        
        # Populate Name
        self.entries["Customer Name"].delete(0, tk.END)
        self.entries["Customer Name"].insert(0, str(row_data[0]))
        
        # Populate Phone
        self.entries["Phone Number"].delete(0, tk.END)
        self.entries["Phone Number"].insert(0, str(row_data[7]))
        
        # Populate ID Number
        self.entries["ID Number"].delete(0, tk.END)
        self.entries["ID Number"].insert(0, str(row_data[8]))
        
        # Room dropdown
        current_room = row_data[1]
        temp_rooms = sorted(list(set(self.available_rooms + [current_room])))
        self.entries["Room"].config(values=temp_rooms)
        self.entries["Room"].set(current_room)
        
        # Payment Status
        self.entries["Payment Status"].set(row_data[4])
        
        # Dates - Parse from raw strings
        try:
            d1 = datetime.strptime(row_data[9], "%Y-%m-%d")
            d2 = datetime.strptime(row_data[10], "%Y-%m-%d")
            self.entries["Check-in Date"].set_date(d1)
            self.entries["Check-out Date"].set_date(d2)
            self.entries["Number of Days"].set(str(row_data[11]))
        except: pass
        
        self.calculate_cost()

    def search_bookings(self, query):
        query = query.lower()
        if not query:
            self.display_data = [list(r) for r in self.all_data]
        else:
            self.display_data = [list(r) for r in self.all_data if any(query in str(v).lower() for v in r)]
        self.update_table()

    def clear_form(self):
        self.editing_id = None
        self.submit_btn.config(text="Add Reservation", bg=self.COLORS["accent"])
        for name, entry in self.entries.items():
            if isinstance(entry, tk.Entry):
                entry.config(state="normal")
                entry.delete(0, tk.END)
                if name == "Total Cost": entry.config(state="readonly")
            elif isinstance(entry, ttk.Combobox):
                entry.set('')
            elif isinstance(entry, DateEntry):
                entry.set_date(datetime.now())
        
        self.refresh_room_data()
        self.entries["Room"].config(values=self.available_rooms)
        if self.available_rooms: self.entries["Room"].current(0)
        self.entries["Number of Days"].current(0)
        self.calculate_cost()
