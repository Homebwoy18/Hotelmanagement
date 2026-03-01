# Meals & Services POS Page
import tkinter as tk
from tkinter import ttk, messagebox
import database

class InventoryPage(tk.Frame): # Keeping class name for compatibility
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
            "info": "#3B82F6",
            "money_bg": "#FFFFFF",
            "money_fg": "#000000"
        }
        
        super().__init__(parent, bg=self.COLORS["bg"])
        self.items_list = []
        self.active_bookings = []
        
        # UI References
        self.pos_card = None
        self.balance_info = None
        self.items_table_body = None
        
        self.setup_ui()
        self.refresh_all()

    def refresh_all(self):
        self.items_list = database.get_inventory_items()
        self.active_bookings = database.get_active_reservations()
        
        # Update POS dropdowns
        if hasattr(self, 'pos_item_selector'):
            self.pos_item_selector['values'] = [f"{i['name']} (GH₵ {i['price']})" for i in self.items_list]
        if hasattr(self, 'pos_room_selector'):
            self.pos_room_selector['values'] = [f"Room {b['room_number']} - {b['guest_name']}" for b in self.active_bookings]
        
        self.update_items_table()
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

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Mousewheel Support
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Main Container inside scrollable frame
        container = tk.Frame(self.scrollable_frame, bg=self.COLORS["bg"], padx=30, pady=20)
        container.pack(fill="both", expand=True)
        
        # 1. Header
        header = tk.Frame(container, bg=self.COLORS["bg"])
        header.pack(fill="x", pady=(0, 20))
        tk.Label(header, text="Meals & Services", font=("Segoe UI", 24, "bold"), 
                 fg=self.COLORS["text_primary"], bg=self.COLORS["bg"]).pack(side="left")

        # 2. Main Grid (POS + Menu)
        main_grid = tk.Frame(container, bg=self.COLORS["bg"])
        main_grid.pack(fill="both", expand=True)
        main_grid.columnconfigure(0, weight=1, minsize=400) # POS Card
        main_grid.columnconfigure(1, weight=2) # Menu Table

        # --- LEFT: POS CARD ---
        self.pos_card = tk.Frame(main_grid, bg=self.COLORS["card"], padx=30, pady=30,
                            highlightbackground=self.COLORS["border"], highlightthickness=1)
        self.pos_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        tk.Label(self.pos_card, text="🛒 Quick Sell", font=("Segoe UI", 18, "bold"), 
                 fg=self.COLORS["accent"], bg=self.COLORS["card"]).pack(anchor="w", pady=(0, 20))

        # Service / Payment Selection
        tk.Label(self.pos_card, text="Sale Method", font=("Segoe UI", 10, "bold"), 
                 fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).pack(anchor="w")
        
        method_frame = tk.Frame(self.pos_card, bg=self.COLORS["card"])
        method_frame.pack(fill="x", pady=(5, 20))
        
        self.pay_method_var = tk.StringVar(value="Instant")
        tk.Radiobutton(method_frame, text="Restaurant (Instant)", variable=self.pay_method_var, value="Instant",
                       bg=self.COLORS["card"], fg="white", selectcolor=self.COLORS["bg"], 
                       activebackground=self.COLORS["card"], activeforeground="white",
                       command=self.toggle_pos_fields).pack(side="left", padx=(0, 10))
        tk.Radiobutton(method_frame, text="Room Charge", variable=self.pay_method_var, value="Room Charge",
                       bg=self.COLORS["card"], fg="white", selectcolor=self.COLORS["bg"],
                       activebackground=self.COLORS["card"], activeforeground="white",
                       command=self.toggle_pos_fields).pack(side="left")

        # Item Selector
        tk.Label(self.pos_card, text="Select Meal", font=("Segoe UI", 10), 
                 fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).pack(anchor="w")
        self.pos_item_selector = ttk.Combobox(self.pos_card, font=("Segoe UI", 12), state="readonly")
        self.pos_item_selector.pack(fill="x", pady=(5, 15))
        self.pos_item_selector.bind("<<ComboboxSelected>>", self.on_item_selected)

        # Quantity & Price Row
        qp_row = tk.Frame(self.pos_card, bg=self.COLORS["card"])
        qp_row.pack(fill="x", pady=(0, 15))
        qp_row.columnconfigure(0, weight=1)
        qp_row.columnconfigure(1, weight=1)

        tk.Label(qp_row, text="Quantity", font=("Segoe UI", 10), 
                 fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).grid(row=0, column=0, sticky="w")
        self.pos_qty = tk.Spinbox(qp_row, from_=1, to=100, font=("Segoe UI", 12), bg="#374151", fg="white", borderwidth=0)
        self.pos_qty.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=5, ipady=5)

        tk.Label(qp_row, text="Price (Edit for Service)", font=("Segoe UI", 10), 
                 fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).grid(row=0, column=1, sticky="w")
        self.pos_price_entry = tk.Entry(qp_row, font=("Segoe UI", 12, "bold"), bg=self.COLORS["money_bg"], fg=self.COLORS["money_fg"], borderwidth=0)
        self.pos_price_entry.grid(row=1, column=1, sticky="ew", pady=5, ipady=5)

        # Room Selector (Dynamic)
        self.room_container = tk.Frame(self.pos_card, bg=self.COLORS["card"])
        # Hidden initially
        tk.Label(self.room_container, text="Select Room Number", font=("Segoe UI", 10), 
                 fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).pack(anchor="w")
        self.pos_room_selector = ttk.Combobox(self.room_container, font=("Segoe UI", 12), state="readonly")
        self.pos_room_selector.pack(fill="x", pady=(5, 10))
        self.pos_room_selector.bind("<<ComboboxSelected>>", lambda e: self.update_balance_label())

        # Balance Info Card
        self.balance_card = tk.Frame(self.pos_card, bg=self.COLORS["warning"], padx=15, pady=10)
        self.balance_info = tk.Label(self.balance_card, text="", font=("Segoe UI", 11, "bold"),
                                     fg="black", bg=self.COLORS["warning"])
        self.balance_info.pack()
        
        # Sale Button
        tk.Button(self.pos_card, text="Confirm Sale", font=("Segoe UI", 14, "bold"),
                  fg="white", bg=self.COLORS["success"], bd=0, pady=15, cursor="hand2",
                  command=self.process_sale).pack(fill="x", pady=(30, 0))

        # --- RIGHT: MEAL MENU ---
        menu_card = tk.Frame(main_grid, bg=self.COLORS["card"],
                            highlightbackground=self.COLORS["border"], highlightthickness=1)
        menu_card.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        
        # Menu Header
        menu_add_bar = tk.Frame(menu_card, bg=self.COLORS["sidebar"], padx=20, pady=20)
        menu_add_bar.pack(fill="x")
        tk.Label(menu_add_bar, text="🍱 Meal Menu", font=("Segoe UI", 14, "bold"), 
                 fg=self.COLORS["text_primary"], bg=self.COLORS["sidebar"]).pack(side="left")
        tk.Button(menu_add_bar, text="+ Create New Meal", font=("Segoe UI", 10, "bold"),
                  fg="white", bg=self.COLORS["accent"], bd=0, padx=15, pady=8, cursor="hand2",
                  command=self.add_meal_dialog).pack(side="right")

        # Menu Table Body
        table_cols = tk.Frame(menu_card, bg=self.COLORS["sidebar"], pady=12, padx=20)
        table_cols.pack(fill="x")
        for i, txt in enumerate(["MEAL NAME", "PRICE", "ACTIONS"]):
            tk.Label(table_cols, text=txt, font=("Segoe UI", 9, "bold"), bg=self.COLORS["sidebar"], fg=self.COLORS["accent"]).grid(row=0, column=i, sticky="ew")
            table_cols.grid_columnconfigure(i, weight=1 if i < 2 else 0)

        self.items_table_body = tk.Frame(menu_card, bg=self.COLORS["bg"])
        self.items_table_body.pack(fill="both", expand=True)

        # --- BOTTOM: TRANSACTIONS LOG ---
        tk.Label(container, text="📜 Transaction History", font=("Segoe UI", 16, "bold"), 
                 fg=self.COLORS["accent"], bg=self.COLORS["bg"]).pack(anchor="w", pady=(30, 15))
        
        log_card = tk.Frame(container, bg=self.COLORS["card"], highlightbackground=self.COLORS["border"], highlightthickness=1)
        log_card.pack(fill="both", expand=True)
        
        log_header = tk.Frame(log_card, bg=self.COLORS["sidebar"], pady=12, padx=20)
        log_header.pack(fill="x")
        headers = ["ID", "ITEM", "QTY", "TOTAL", "METHOD", "DATE", "GUEST", "ROOM"]
        for i, text in enumerate(headers):
            tk.Label(log_header, text=text, font=("Segoe UI", 9, "bold"), bg=self.COLORS["sidebar"], fg=self.COLORS["accent"]).grid(row=0, column=i, sticky="ew")
            log_header.grid_columnconfigure(i, weight=1)

        self.sales_log_body = tk.Frame(log_card, bg=self.COLORS["card"])
        self.sales_log_body.pack(fill="both", expand=True)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def toggle_pos_fields(self):
        if self.pay_method_var.get() == "Room Charge":
            self.room_container.pack(fill="x", pady=(10, 0))
            self.balance_card.pack(fill="x", pady=(10, 0))
            self.update_balance_label()
        else:
            self.room_container.pack_forget()
            self.balance_card.pack_forget()
        
    def on_item_selected(self, event=None):
        idx = self.pos_item_selector.current()
        if idx >= 0:
            price = self.items_list[idx]['price']
            self.pos_price_entry.config(state="normal")
            self.pos_price_entry.delete(0, tk.END)
            self.pos_price_entry.insert(0, str(price))
            
    def update_balance_label(self):
        if self.pay_method_var.get() == "Room Charge":
            idx = self.pos_room_selector.current()
            if idx >= 0:
                res = self.active_bookings[idx]
                balance = database.get_reservation_balance(res['id'])
                self.balance_info.config(text=f"Room {res['room_number']}: {res['guest_name']} | Bill: GH₵ {balance:,.2f}")
            else:
                self.balance_info.config(text="Select room to view balance")

    def update_items_table(self):
        if not self.items_table_body: return
        for widget in self.items_table_body.winfo_children(): widget.destroy()

        for item in self.items_list:
            r = tk.Frame(self.items_table_body, bg=self.COLORS["card"], pady=12, padx=20)
            r.pack(fill="x")
            
            tk.Label(r, text=item['name'], font=("Segoe UI", 11), bg=self.COLORS["card"], fg="white").grid(row=0, column=0, sticky="w")
            tk.Label(r, text=f"GH₵ {item['price']:,.2f}", font=("Segoe UI", 11, "bold"), bg=self.COLORS["card"], fg=self.COLORS["success"]).grid(row=0, column=1, sticky="w")
            
            actions = tk.Frame(r, bg=self.COLORS["card"])
            actions.grid(row=0, column=2, sticky="e")
            tk.Button(actions, text="🗑 DELETE", font=("Segoe UI", 9, "bold"), bg=self.COLORS["danger"], fg="white", 
                      bd=0, padx=10, pady=4, cursor="hand2", command=lambda i=item['id']: self.delete_item(i)).pack()
            
            r.grid_columnconfigure(0, weight=1)
            r.grid_columnconfigure(1, weight=1)
            r.grid_columnconfigure(2, weight=0)
            
            tk.Frame(self.items_table_body, bg=self.COLORS["border"], height=1).pack(fill="x")

    def delete_item(self, iid):
        if database.delete_inventory_item(iid): 
            self.refresh_all()

    def add_meal_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add New Meal")
        dialog.geometry("400x350")
        dialog.configure(bg=self.COLORS["bg"])
        dialog.transient(self.winfo_toplevel()) # Make it stay on top correctly
        dialog.grab_set() # Lock focus
        
        main = tk.Frame(dialog, bg=self.COLORS["bg"], padx=30, pady=30)
        main.pack(fill="both", expand=True)

        tk.Label(main, text="Add New Meal", font=("Segoe UI", 16, "bold"), fg="white", bg=self.COLORS["bg"]).pack(pady=(0, 20))

        tk.Label(main, text="Meal Name", fg=self.COLORS["text_secondary"], bg=self.COLORS["bg"]).pack(anchor="w")
        name_entry = tk.Entry(main, font=("Segoe UI", 11), bg=self.COLORS["card"], fg="white", borderwidth=0)
        name_entry.pack(fill="x", pady=(5, 15), ipady=8)

        tk.Label(main, text="Price (GH₵)", fg=self.COLORS["text_secondary"], bg=self.COLORS["bg"]).pack(anchor="w")
        price_entry = tk.Entry(main, font=("Segoe UI", 11), bg=self.COLORS["card"], fg="white", borderwidth=0)
        price_entry.pack(fill="x", pady=(5, 15), ipady=8)

        def save():
            try:
                n = name_entry.get().strip()
                p_str = price_entry.get().replace('GH₵', '').strip()
                p = float(p_str)
                if not n: throw
                if database.add_inventory_item(n, "Meal", p):
                    self.refresh_all()
                    dialog.destroy()
                    messagebox.showinfo("Success", f"'{n}' added to menu.")
            except: messagebox.showwarning("Error", "Please enter a valid meal name and price.")

        tk.Button(main, text="Save Meal", font=("Segoe UI", 12, "bold"), bg=self.COLORS["accent"], fg="white", 
                  bd=0, pady=12, cursor="hand2", command=save).pack(fill="x", pady=(10, 0))

    def process_sale(self):
        item_idx = self.pos_item_selector.current()
        if item_idx < 0: 
            messagebox.showwarning("Selection Required", "Please select a meal first.")
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

    def update_sales_log(self):
        if not hasattr(self, 'sales_log_body'): return
        for widget in self.sales_log_body.winfo_children(): widget.destroy()
        
        sales = database.get_sales_report()
        for s in sales[:15]:
            r = tk.Frame(self.sales_log_body, bg=self.COLORS["card"], pady=12, padx=20)
            r.pack(fill="x")
            date_str = s['sale_date'].split('.')[0] if s['sale_date'] else "N/A"
            data = [s['id'], s['name'], s['quantity'], f"GH₵ {s['total_cost']:,.2f}", s['payment_method'], date_str, s['guest_name'] or "-", s['room_number'] or "-"]
            for i, val in enumerate(data):
                r.grid_columnconfigure(i, weight=1)
                if i == 4: # Payment Method Badge
                    color = self.COLORS["success"] if "Instant" in str(val) else self.COLORS["info"]
                    badge_container = tk.Frame(r, bg=self.COLORS["card"])
                    badge_container.grid(row=0, column=i, sticky="ew")
                    badge_bg = tk.Frame(badge_container, bg=color, padx=10, pady=2)
                    badge_bg.pack()
                    tk.Label(badge_bg, text=str(val).upper(), font=("Segoe UI", 8, "bold"), fg="white", bg=color).pack()
                else:
                    tk.Label(r, text=val, font=("Segoe UI", 10), bg=self.COLORS["card"], 
                             fg="white" if i != 3 else self.COLORS["success"]).grid(row=0, column=i, sticky="ew")
            tk.Frame(self.sales_log_body, bg=self.COLORS["border"], height=1).pack(fill="x")
