# Meals & Services POS Page
import tkinter as tk
from tkinter import ttk, messagebox
import database
from Views.theme import COLORS

class InventoryPage(tk.Frame): # Keeping class name for compatibility
    def __init__(self, parent):
        self.COLORS = COLORS
        
        super().__init__(parent, bg=self.COLORS["bg"])
        self.items_list = []
        self.active_bookings = []
        
        # UI References
        self.pos_card = None
        self.balance_info = None
        self.items_table_body = None
        self.pos_item_selector = None
        self.pos_room_selector = None
        self.log_canvas = None
        self.sales_log_body = None
        self.log_pagination_frame = None
        
        # Pagination for Sales Log
        self.sales_page = 0
        self.sales_rows_per_page = 10
        self.sales_weights = [10, 20, 10, 15, 15, 20, 15, 10]
        self.sales_cols = ["ID", "ITEM", "QTY", "TOTAL", "METHOD", "DATE", "GUEST", "ROOM"]
        
        # Search & Data
        self.search_var = tk.StringVar()
        self.all_sales = []
        self.display_sales = []
        
        # POS State
        self.pay_method_var = tk.StringVar(value="Instant")
        self.pos_qty = None
        self.pos_price_entry = None
        self.pos_room_selector = None
        self.room_container = None
        self.balance_card = None
        self.balance_info = None
        
        self.setup_ui()
        self.refresh_all()
        
        # Unbind mousewheel when destroyed to prevent TclError
        self.bind("<Destroy>", self.on_destroy)

    def on_destroy(self, event):
        if event.widget == self:
            try:
                self.unbind_all("<MouseWheel>")
            except: pass

    def refresh_all(self):
        self.items_list = database.get_inventory_items()
        self.active_bookings = database.get_active_reservations()
        
        if hasattr(self, 'pos_item_selector'):
            self.pos_item_selector['values'] = [f"{i['name']} (GH₵ {i['price']})" for i in self.items_list]
        if hasattr(self, 'pos_room_selector'):
            self.pos_room_selector['values'] = [f"Room {b['room_number']} - {b['guest_name']}" for b in self.active_bookings]
        
        self.update_sales_log()
        self.update_balance_label()

    def setup_ui(self):
        # Create Canvas for Global Scrolling
        self.canvas = tk.Canvas(self, bg=self.COLORS["bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.COLORS["bg"])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y", padx=(10, 0)) # Add padding to scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)

        # Mousewheel Support
        def _on_mousewheel(event):
            try:
                if self.canvas and self.canvas.winfo_exists():
                    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except: pass
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Main Container
        container = tk.Frame(self.scrollable_frame, bg=self.COLORS["bg"], padx=40, pady=30)
        container.pack(fill="both", expand=True)
        
        # 1. Header
        header = tk.Frame(container, bg=self.COLORS["bg"])
        header.pack(fill="x", pady=(0, 30))
        tk.Label(header, text="🛒 POS & Sales", font=("Segoe UI", 24, "bold"), 
                 fg=self.COLORS["text_primary"], bg=self.COLORS["bg"]).pack(side="left")

        # 2. POS Card (Full Width for better space)
        self.pos_card = tk.Frame(container, bg=self.COLORS["card"], padx=40, pady=40,
                            highlightbackground=self.COLORS["border"], highlightthickness=1)
        self.pos_card.pack(fill="x", pady=(0, 40))
        
        tk.Label(self.pos_card, text="🛒 Quick Sell & Room Charge", font=("Segoe UI", 18, "bold"), 
                 fg=self.COLORS["accent"], bg=self.COLORS["card"]).pack(anchor="w", pady=(0, 30))

        # Split form into two columns
        form_row1 = tk.Frame(self.pos_card, bg=self.COLORS["card"])
        form_row1.pack(fill="x", pady=(0, 20))
        form_row1.columnconfigure(0, weight=1)
        form_row1.columnconfigure(1, weight=1)

        # Left Side: Sale Method
        method_col = tk.Frame(form_row1, bg=self.COLORS["card"])
        method_col.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        tk.Label(method_col, text="Sale Method", font=("Segoe UI", 11, "bold"), 
                 fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).pack(anchor="w", pady=(0, 10))
        
        self.pay_method_var.set("Instant")
        tk.Radiobutton(method_col, text="Restaurant (Instant Pay)", variable=self.pay_method_var, value="Instant",
                       bg=self.COLORS["card"], fg="white", selectcolor=self.COLORS["bg"], 
                       activebackground=self.COLORS["card"], activeforeground="white",
                       font=("Segoe UI", 10), command=self.toggle_pos_fields).pack(side="left", padx=(0, 15))
        tk.Radiobutton(method_col, text="Room Charge (Bill to Guest)", variable=self.pay_method_var, value="Room Charge",
                       bg=self.COLORS["card"], fg="white", selectcolor=self.COLORS["bg"],
                       activebackground=self.COLORS["card"], activeforeground="white",
                       font=("Segoe UI", 10), command=self.toggle_pos_fields).pack(side="left")

        # Right Side: Item Selection
        item_col = tk.Frame(form_row1, bg=self.COLORS["card"])
        item_col.grid(row=0, column=1, sticky="nsew")
        
        tk.Label(item_col, text="Select Item", font=("Segoe UI", 11, "bold"), 
                 fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).pack(anchor="w", pady=(0, 5))
        self.pos_item_selector = ttk.Combobox(item_col, font=("Segoe UI", 12), state="readonly")
        self.pos_item_selector.pack(fill="x", ipady=5)
        self.pos_item_selector.bind("<<ComboboxSelected>>", self.on_item_selected)

        # Row 2: Qty, Price, Room
        form_row2 = tk.Frame(self.pos_card, bg=self.COLORS["card"])
        form_row2.pack(fill="x")
        form_row2.columnconfigure(0, weight=1)
        form_row2.columnconfigure(1, weight=1)
        form_row2.columnconfigure(2, weight=1)

        # Qty
        tk.Label(form_row2, text="Quantity", font=("Segoe UI", 11, "bold"), 
                 fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).grid(row=0, column=0, sticky="w")
        self.pos_qty = tk.Spinbox(form_row2, from_=1, to=100, font=("Segoe UI", 12), bg="#374151", fg="white", borderwidth=0)
        self.pos_qty.grid(row=1, column=0, sticky="ew", padx=(0, 20), pady=10, ipady=8)

        # Price
        tk.Label(form_row2, text="Unit Price (GH₵)", font=("Segoe UI", 11, "bold"), 
                 fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).grid(row=0, column=1, sticky="w")
        self.pos_price_entry = tk.Entry(form_row2, font=("Segoe UI", 12, "bold"), bg=self.COLORS["money_bg"], fg=self.COLORS["money_fg"], borderwidth=0)
        self.pos_price_entry.grid(row=1, column=1, sticky="ew", padx=(0, 20), pady=10, ipady=8)

        # Room Selector (Dynamic)
        self.room_container = tk.Frame(form_row2, bg=self.COLORS["card"])
        self.room_container.grid(row=0, column=2, rowspan=2, sticky="nsew")
        
        tk.Label(self.room_container, text="Guest Room", font=("Segoe UI", 11, "bold"), 
                 fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).pack(anchor="w", pady=(0, 5))
        self.pos_room_selector = ttk.Combobox(self.room_container, font=("Segoe UI", 12), state="readonly")
        self.pos_room_selector.pack(fill="x", ipady=5)
        self.pos_room_selector.bind("<<ComboboxSelected>>", lambda e: self.update_balance_label())
        self.room_container.grid_remove() # Hidden initially

        # Balance & Confirm Action
        action_row = tk.Frame(self.pos_card, bg=self.COLORS["card"])
        action_row.pack(fill="x", pady=(30, 0))
        
        self.balance_card = tk.Frame(action_row, bg=self.COLORS["warning"], padx=20, pady=10)
        self.balance_info = tk.Label(self.balance_card, text="", font=("Segoe UI", 12, "bold"), fg="black", bg=self.COLORS["warning"])
        self.balance_info.pack()
        self.balance_card.pack_forget()

        tk.Button(action_row, text="Confirm Transaction", font=("Segoe UI", 14, "bold"),
                  fg="white", bg=self.COLORS["success"], bd=0, pady=15, cursor="hand2",
                  command=self.process_sale).pack(side="right", padx=(20, 0), ipadx=40)

        # --- TRANSACTION LOG ---
        log_header_row = tk.Frame(container, bg=self.COLORS["bg"])
        log_header_row.pack(fill="x", pady=(20, 15))
        
        tk.Label(log_header_row, text="📜 Recent Sales & Transactions", font=("Segoe UI", 18, "bold"), 
                 fg=self.COLORS["accent"], bg=self.COLORS["bg"]).pack(side="left")
        
        # Search for Sales Log
        search_frame = tk.Frame(log_header_row, bg=self.COLORS["card"], padx=10, pady=5, 
                                highlightbackground=self.COLORS["border"], highlightthickness=1)
        search_frame.pack(side="right")
        tk.Label(search_frame, text="🔍", bg=self.COLORS["card"], fg=self.COLORS["text_secondary"]).pack(side="left")
        log_search = tk.Entry(search_frame, textvariable=self.search_var, bg=self.COLORS["card"], 
                              fg=self.COLORS["text_primary"], border=0, font=("Segoe UI", 10), width=30)
        log_search.pack(side="left", padx=5)
        self.search_var.trace_add("write", lambda *args: self.search_sales(self.search_var.get()))
        
        log_card = tk.Frame(container, bg=self.COLORS["card"], highlightbackground=self.COLORS["border"], highlightthickness=1)
        log_card.pack(fill="both", expand=True)
        
        # Structural fix for exact column alignment: Header and Canvas share inner_container
        # Scrollbar is outside inner_container
        self.log_scrollbar = ttk.Scrollbar(log_card, orient="vertical", command=None)
        self.log_scrollbar.pack(side="right", fill="y")
        
        inner_container = tk.Frame(log_card, bg=self.COLORS["card"])
        inner_container.pack(side="left", fill="both", expand=True)

        # Log Table Header (Inside inner_container)
        self.log_header = tk.Frame(inner_container, bg=self.COLORS["sidebar"], pady=15, padx=25)
        self.log_header.pack(fill="x")
        for i, text in enumerate(self.sales_cols):
            tk.Label(self.log_header, text=text, font=("Segoe UI", 9, "bold"), bg=self.COLORS["sidebar"], fg=self.COLORS["accent"]).grid(row=0, column=i, sticky="ew")
            self.log_header.grid_columnconfigure(i, weight=int(self.sales_weights[i]))

        # Scrollable Log Body (Inside inner_container)
        self.log_canvas = tk.Canvas(inner_container, bg=self.COLORS["card"], highlightthickness=0, height=500)
        self.log_canvas.pack(fill="both", expand=True)
        
        self.log_scrollbar.config(command=self.log_canvas.yview)
        self.log_canvas.configure(yscrollcommand=self.log_scrollbar.set)

        self.sales_log_body = tk.Frame(self.log_canvas, bg=self.COLORS["card"])
        self.log_canvas.create_window((0, 0), window=self.sales_log_body, anchor="nw")
        
        def _on_log_configure(event):
            self.log_canvas.itemconfig(self.log_canvas.find_all()[0], width=event.width)
        self.log_canvas.bind("<Configure>", _on_log_configure)

        # Pagination Footer
        self.log_pagination_frame = tk.Frame(container, bg=self.COLORS["bg"], pady=20)
        self.log_pagination_frame.pack(fill="x")

    def toggle_pos_fields(self):
        if self.pay_method_var.get() == "Room Charge":
            self.room_container.grid()
            self.balance_card.pack(side="left")
            self.update_balance_label()
        else:
            self.room_container.grid_remove()
            self.balance_card.pack_forget()
        
    def on_item_selected(self, event=None):
        idx = self.pos_item_selector.current()
        if idx >= 0:
            price = self.items_list[idx]['price']
            self.pos_price_entry.delete(0, tk.END)
            self.pos_price_entry.insert(0, str(price))
            
    def update_balance_label(self):
        if self.pay_method_var.get() == "Room Charge":
            idx = self.pos_room_selector.current()
            if idx >= 0:
                res = self.active_bookings[idx]
                balance = database.get_reservation_balance(res['id'])
                self.balance_info.config(text=f"Guest: {res['guest_name']} | Room Balance: GH₵ {balance:,.2f}")
            else:
                self.balance_info.config(text="Select room to view balance")

    def process_sale(self):
        item_idx = self.pos_item_selector.current()
        if item_idx < 0: 
            messagebox.showwarning("Selection Required", "Please select an item first.")
            return
        try:
            qty = int(self.pos_qty.get())
            price = float(self.pos_price_entry.get())
            method = self.pay_method_var.get()
            res_id = None
            if method == "Room Charge":
                ridx = self.pos_room_selector.current()
                if ridx < 0: 
                    messagebox.showwarning("Room Required", "Please select a room for room charge.")
                    return
                res_id = self.active_bookings[ridx]['id']
            
            if database.record_sale_manual(self.items_list[item_idx]['id'], qty, method, price, res_id):
                messagebox.showinfo("Success", "Transaction recorded!")
                self.refresh_all()
        except Exception as e: messagebox.showerror("Error", f"Invalid input: {e}")

    def search_sales(self, query):
        query = query.lower().strip()
        if not query:
            self.display_sales = list(self.all_sales)
        else:
            self.display_sales = []
            for s in self.all_sales:
                searchable = f"{s['id']} {s['name']} {s['payment_method']} {s['guest_name']} {s['room_number']}".lower()
                if query in searchable:
                    self.display_sales.append(s)
        self.sales_page = 0
        self.update_sales_log()

    def update_sales_log(self):
        if not hasattr(self, 'sales_log_body'): return
        for widget in self.sales_log_body.winfo_children(): widget.destroy()
        
        self.all_sales = database.get_sales_report()
        # Initial flow or empty search
        if not self.search_var.get().strip():
            self.display_sales = list(self.all_sales)
        
        total_items = len(self.display_sales)
        total_pages = max(1, (total_items + self.sales_rows_per_page - 1) // self.sales_rows_per_page)
        
        if self.sales_page >= total_pages: self.sales_page = total_pages - 1
        start = self.sales_page * self.sales_rows_per_page
        end = start + self.sales_rows_per_page
        page_data = self.display_sales[start:end]

        for s in page_data:
            r = tk.Frame(self.sales_log_body, bg=self.COLORS["card"], pady=15, padx=25)
            r.pack(fill="x")
            date_str = s['sale_date'].split('.')[0] if s['sale_date'] else "N/A"
            data = [s['id'], s['name'], s['quantity'], f"GH₵ {s['total_cost']:,.2f}", s['payment_method'], date_str, s['guest_name'] or "-", s['room_number'] or "-"]
            
            for i, val in enumerate(data):
                r.grid_columnconfigure(i, weight=int(self.sales_weights[i]))
                if i == 4: # Payment Method Badge
                    color = self.COLORS["success"] if "Instant" in str(val) else self.COLORS["info"]
                    badge_container = tk.Frame(r, bg=self.COLORS["card"])
                    badge_container.grid(row=0, column=i, sticky="ew")
                    badge_bg = tk.Frame(badge_container, bg=color, padx=10, pady=2)
                    badge_bg.pack()
                    tk.Label(badge_bg, text=str(val).upper(), font=("Segoe UI", 8, "bold"), fg="white", bg=color).pack()
                else:
                    tk.Label(r, text=val, font=("Segoe UI", 10), bg=self.COLORS["card"], 
                             fg="white" if i != 3 else self.COLORS["success"], anchor="center" if i > 1 else "w").grid(row=0, column=i, sticky="ew")
            tk.Frame(self.sales_log_body, bg=self.COLORS["border"], height=1).pack(fill="x")

        self.update_log_pagination_controls(total_pages)
        self.sales_log_body.update_idletasks()
        self.log_canvas.config(scrollregion=self.log_canvas.bbox("all"))

    def update_log_pagination_controls(self, total_pages):
        for widget in self.log_pagination_frame.winfo_children(): widget.destroy()
        inner_p = tk.Frame(self.log_pagination_frame, bg=self.COLORS["bg"])
        inner_p.pack()

        prev_btn = tk.Button(inner_p, text="← Previous", font=("Segoe UI", 10, "bold"),
                            fg="white" if self.sales_page > 0 else self.COLORS["text_secondary"],
                            bg=self.COLORS["sidebar"] if self.sales_page > 0 else self.COLORS["bg"],
                            bd=0, padx=15, pady=8, cursor="hand2" if self.sales_page > 0 else "arrow",
                            command=self.prev_sales_page)
        prev_btn.pack(side="left", padx=10)

        page_lbl = tk.Label(inner_p, text=f"Page {self.sales_page + 1} of {total_pages}",
                           font=("Segoe UI", 11), fg=self.COLORS["text_primary"], bg=self.COLORS["bg"])
        page_lbl.pack(side="left", padx=20)

        next_btn = tk.Button(inner_p, text="Next →", font=("Segoe UI", 10, "bold"),
                            fg="white" if self.sales_page < total_pages - 1 else self.COLORS["text_secondary"],
                            bg=self.COLORS["sidebar"] if self.sales_page < total_pages - 1 else self.COLORS["bg"],
                            bd=0, padx=15, pady=8, cursor="hand2" if self.sales_page < total_pages - 1 else "arrow",
                            command=self.next_sales_page)
        next_btn.pack(side="left", padx=10)

    def prev_sales_page(self):
        if self.sales_page > 0:
            self.sales_page -= 1
            self.update_sales_log()

    def next_sales_page(self):
        total_items = len(self.display_sales)
        total_pages = (total_items + self.sales_rows_per_page - 1) // self.sales_rows_per_page
        if self.sales_page < total_pages - 1:
            self.sales_page += 1
            self.update_sales_log()
