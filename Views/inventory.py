# Inventory Management & POS Page
import tkinter as tk
from tkinter import ttk, messagebox
import database

class InventoryPage(tk.Frame):
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
        self.items_list = []
        self.active_bookings = []
        self.setup_ui()
        self.refresh_all()

    def refresh_all(self):
        self.items_list = database.get_inventory_items()
        self.active_bookings = database.get_active_reservations()
        
        # Update POS dropdowns
        self.pos_item_selector['values'] = [f"{i['name']} (GH₵ {i['price']})" for i in self.items_list]
        self.pos_guest_selector['values'] = [f"{b['guest_name']} - Room {b['room_number']}" for b in self.active_bookings]
        
        self.update_items_table()
        self.update_sales_log()

    def setup_ui(self):
        container = tk.Frame(self, bg=self.COLORS["bg"], padx=30, pady=30)
        container.pack(fill="both", expand=True)
        
        header = tk.Frame(container, bg=self.COLORS["bg"])
        header.pack(fill="x", pady=(0, 20))
        tk.Label(header, text="Inventory & Services POS", font=("Segoe UI", 24, "bold"), 
                 fg=self.COLORS["text_primary"], bg=self.COLORS["bg"]).pack(side="left")

        # Layout: Left column (POS), Right column (Item Management)
        main_grid = tk.Frame(container, bg=self.COLORS["bg"])
        main_grid.pack(fill="both", expand=True)
        main_grid.columnconfigure(0, weight=1) # POS
        main_grid.columnconfigure(1, weight=1) # Items

        # --- LEFT: POS SECTION ---
        pos_card = tk.Frame(main_grid, bg=self.COLORS["card"], padx=25, pady=25, 
                           highlightbackground=self.COLORS["border"], highlightthickness=1)
        pos_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        tk.Label(pos_card, text="🛒 Quick Sale / Service", font=("Segoe UI", 16, "bold"), 
                 fg=self.COLORS["accent"], bg=self.COLORS["card"]).pack(anchor="w", pady=(0, 20))

        # Item Selector
        tk.Label(pos_card, text="Select Item", font=("Segoe UI", 10), 
                 fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).pack(anchor="w")
        self.pos_item_selector = ttk.Combobox(pos_card, font=("Segoe UI", 11), state="readonly")
        self.pos_item_selector.pack(fill="x", pady=(5, 15))

        # Quantity
        tk.Label(pos_card, text="Quantity", font=("Segoe UI", 10), 
                 fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).pack(anchor="w")
        self.pos_qty = tk.Spinbox(pos_card, from_=1, to=100, font=("Segoe UI", 11), bg="#374151", fg="white", borderwidth=0)
        self.pos_qty.pack(fill="x", pady=(5, 15), ipady=5)

        # Payment Method
        tk.Label(pos_card, text="Payment Method", font=("Segoe UI", 10), 
                 fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).pack(anchor="w")
        self.pay_method_var = tk.StringVar(value="Instant")
        pay_frame = tk.Frame(pos_card, bg=self.COLORS["card"])
        pay_frame.pack(fill="x", pady=(5, 15))
        
        tk.Radiobutton(pay_frame, text="Instant Pay", variable=self.pay_method_var, value="Instant",
                       bg=self.COLORS["card"], fg="white", selectcolor=self.COLORS["bg"], 
                       activebackground=self.COLORS["card"], activeforeground="white",
                       command=self.toggle_guest_selector).pack(side="left", padx=(0, 20))
        tk.Radiobutton(pay_frame, text="Bill to Room", variable=self.pay_method_var, value="Room Charge",
                       bg=self.COLORS["card"], fg="white", selectcolor=self.COLORS["bg"],
                       activebackground=self.COLORS["card"], activeforeground="white",
                       command=self.toggle_guest_selector).pack(side="left")

        # Guest Selector (Only for Room Charge)
        self.guest_label = tk.Label(pos_card, text="Select Guest / Room", font=("Segoe UI", 10), 
                                   fg=self.COLORS["text_secondary"], bg=self.COLORS["card"])
        self.pos_guest_selector = ttk.Combobox(pos_card, font=("Segoe UI", 11), state="readonly")
        
        # Sale Button
        tk.Button(pos_card, text="Process Transaction", font=("Segoe UI", 12, "bold"),
                  fg="white", bg=self.COLORS["success"], bd=0, pady=12, cursor="hand2",
                  command=self.process_sale).pack(fill="x", pady=(20, 0))

        # --- RIGHT: ITEM MANAGEMENT ---
        item_card = tk.Frame(main_grid, bg=self.COLORS["card"], padx=25, pady=25,
                            highlightbackground=self.COLORS["border"], highlightthickness=1)
        item_card.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        
        tk.Label(item_card, text="🍱 Manage Inventory Items", font=("Segoe UI", 16, "bold"), 
                 fg=self.COLORS["accent"], bg=self.COLORS["card"]).pack(anchor="w", pady=(0, 20))

        # Quick Add Row
        add_row = tk.Frame(item_card, bg=self.COLORS["card"])
        add_row.pack(fill="x", pady=(0, 20))
        add_row.columnconfigure(0, weight=2)
        add_row.columnconfigure(1, weight=1)
        add_row.columnconfigure(2, weight=1)

        self.new_item_name = tk.Entry(add_row, font=("Segoe UI", 10), bg="#374151", fg="white", borderwidth=0)
        self.new_item_name.grid(row=0, column=0, sticky="ew", padx=2, ipady=5)
        self.new_item_name.insert(0, "Item Name...")

        self.new_item_type = ttk.Combobox(add_row, values=["Restaurant", "Room Service"], font=("Segoe UI", 10), state="readonly")
        self.new_item_type.grid(row=0, column=1, sticky="ew", padx=2)
        self.new_item_type.current(0)

        self.new_item_price = tk.Entry(add_row, font=("Segoe UI", 10), bg="#374151", fg="white", borderwidth=0)
        self.new_item_price.grid(row=0, column=2, sticky="ew", padx=2, ipady=5)
        self.new_item_price.insert(0, "Price")

        tk.Button(item_card, text="+ Add Item to List", font=("Segoe UI", 10, "bold"),
                  fg="white", bg=self.COLORS["accent"], bd=0, pady=8, cursor="hand2",
                  command=self.add_item).pack(fill="x", pady=(0, 20))

        # Items Table
        self.items_table = tk.Frame(item_card, bg=self.COLORS["card"])
        self.items_table.pack(fill="both", expand=True)

    def toggle_guest_selector(self):
        if self.pay_method_var.get() == "Room Charge":
            self.guest_label.pack(anchor="w")
            self.pos_guest_selector.pack(fill="x", pady=(5, 15))
        else:
            self.guest_label.pack_forget()
            self.pos_guest_selector.pack_forget()

    def add_item(self):
        name = self.new_item_name.get()
        i_type = self.new_item_type.get()
        try:
            price = float(self.new_item_price.get())
            if database.add_inventory_item(name, i_type, price):
                messagebox.showinfo("Success", f"{name} added to inventory.")
                self.refresh_all()
                self.new_item_name.delete(0, tk.END)
                self.new_item_price.delete(0, tk.END)
            else: messagebox.showerror("Error", "Could not add item.")
        except: messagebox.showwarning("Warning", "Please enter a valid price.")

    def update_items_table(self):
        for widget in self.items_table.winfo_children(): widget.destroy()
        
        # Header
        h = tk.Frame(self.items_table, bg=self.COLORS["sidebar"], pady=8)
        h.pack(fill="x")
        for i, txt in enumerate(["NAME", "TYPE", "PRICE", ""]):
            tk.Label(h, text=txt, font=("Segoe UI", 9, "bold"), bg=self.COLORS["sidebar"], fg=self.COLORS["accent"]).grid(row=0, column=i, sticky="ew")
            h.grid_columnconfigure(i, weight=1)

        for item in self.items_list:
            r = tk.Frame(self.items_table, bg=self.COLORS["card"], pady=10)
            r.pack(fill="x")
            tk.Label(r, text=item['name'], font=("Segoe UI", 10), bg=self.COLORS["card"], fg="white").grid(row=0, column=0, sticky="ew")
            tk.Label(r, text=item['type'], font=("Segoe UI", 9), bg=self.COLORS["card"], fg=self.COLORS["text_secondary"]).grid(row=0, column=1, sticky="ew")
            tk.Label(r, text=f"GH₵ {item['price']}", font=("Segoe UI", 10, "bold"), bg=self.COLORS["card"], fg=self.COLORS["success"]).grid(row=0, column=2, sticky="ew")
            tk.Button(r, text="🗑", bg=self.COLORS["card"], fg=self.COLORS["danger"], bd=0, 
                      command=lambda i=item['id']: self.delete_item(i)).grid(row=0, column=3)
            r.grid_columnconfigure(0, weight=1)
            r.grid_columnconfigure(1, weight=1)
            r.grid_columnconfigure(2, weight=1)
            r.grid_columnconfigure(3, weight=1)
            tk.Frame(self.items_table, bg=self.COLORS["border"], height=1).pack(fill="x")

    def delete_item(self, iid):
        if database.delete_inventory_item(iid):
            self.refresh_all()

    def process_sale(self):
        item_idx = self.pos_item_selector.current()
        if item_idx < 0:
            messagebox.showwarning("Warning", "Please select an item.")
            return
        
        item_id = self.items_list[item_idx]['id']
        qty = int(self.pos_qty.get())
        method = self.pay_method_var.get()
        res_id = None

        if method == "Room Charge":
            res_idx = self.pos_guest_selector.current()
            if res_idx < 0:
                messagebox.showwarning("Warning", "Select a guest for Room Charge.")
                return
            res_id = self.active_bookings[res_idx]['id']

        if database.record_sale(item_id, qty, method, res_id):
            messagebox.showinfo("Success", "Transaction recorded successfully!")
            self.refresh_all()
            self.update_sales_log()
        else:
            messagebox.showerror("Error", "Transaction failed.")
