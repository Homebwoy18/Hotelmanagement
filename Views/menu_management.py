# Meal Menu Management Page
import tkinter as tk
from tkinter import ttk, messagebox
import database

class MenuManagementPage(tk.Frame):
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
            "danger": "#EF4444"
        }
        
        super().__init__(parent, bg=self.COLORS["bg"])
        self.items_list = []
        
        # Pagination settings
        self.current_page = 0
        self.rows_per_page = 10
        self.weights = [2, 1, 1]
        self.cols = ["MEAL NAME", "PRICE (GH₵)", "ACTIONS"]
        
        self.setup_ui()
        self.refresh_data()
        
        # Unbind mousewheel when destroyed
        self.bind("<Destroy>", self.on_destroy)

    def on_destroy(self, event):
        if event.widget == self:
            try:
                self.unbind_all("<MouseWheel>")
            except: pass

    def refresh_data(self):
        self.items_list = database.get_inventory_items()
        self.update_table()

    def setup_ui(self):
        container = tk.Frame(self, bg=self.COLORS["bg"], padx=40, pady=30)
        container.pack(fill="both", expand=True)

        # Header
        header = tk.Frame(container, bg=self.COLORS["bg"])
        header.pack(fill="x", pady=(0, 25))
        
        tk.Label(header, text="🍱 Meal Menu Management", font=("Segoe UI", 24, "bold"), 
                 fg=self.COLORS["text_primary"], bg=self.COLORS["bg"]).pack(side="left")
        
        # Search
        self.search_var = tk.StringVar()
        search_frame = tk.Frame(header, bg=self.COLORS["card"], padx=10, pady=5, 
                                highlightbackground=self.COLORS["border"], highlightthickness=1)
        search_frame.pack(side="left", padx=30)
        tk.Label(search_frame, text="🔍", bg=self.COLORS["card"], fg=self.COLORS["text_secondary"]).pack(side="left")
        menu_search = tk.Entry(search_frame, textvariable=self.search_var, bg=self.COLORS["card"], 
                               fg=self.COLORS["text_primary"], border=0, font=("Segoe UI", 10), width=30)
        menu_search.pack(side="left", padx=5)
        self.search_var.trace_add("write", lambda *args: self.update_table())

        tk.Button(header, text="+ Create New Meal", font=("Segoe UI", 11, "bold"),
                  fg="white", bg=self.COLORS["accent"], bd=0, padx=20, pady=10, cursor="hand2",
                  command=self.add_meal_dialog).pack(side="right")

        # Table Card
        self.table_card = tk.Frame(container, bg=self.COLORS["card"], 
                               highlightbackground=self.COLORS["border"], highlightthickness=1)
        self.table_card.pack(fill="both", expand=True)

        # Structural fix for exact column alignment: Header and Canvas share inner_container
        # Scrollbar is outside inner_container
        self.table_scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=None)
        self.table_scrollbar.pack(side="right", fill="y")
        
        inner_container = tk.Frame(self.table_card, bg=self.COLORS["card"])
        inner_container.pack(side="left", fill="both", expand=True)

        # Sticky Header (Inside inner_container)
        self.header_frame = tk.Frame(inner_container, bg=self.COLORS["sidebar"], pady=15, padx=25)
        self.header_frame.pack(fill="x")
        for i, txt in enumerate(self.cols):
            tk.Label(self.header_frame, text=txt, font=("Segoe UI", 10, "bold"), 
                     bg=self.COLORS["sidebar"], fg=self.COLORS["accent"]).grid(row=0, column=i, sticky="ew")
            self.header_frame.grid_columnconfigure(i, weight=self.weights[i])

        # Scrollable Table Body (Inside inner_container)
        self.table_canvas = tk.Canvas(inner_container, bg=self.COLORS["card"], highlightthickness=0)
        self.table_canvas.pack(fill="both", expand=True)
        
        self.table_scrollbar.config(command=self.table_canvas.yview)
        self.table_canvas.configure(yscrollcommand=self.table_scrollbar.set)

        self.table_body = tk.Frame(self.table_canvas, bg=self.COLORS["card"])
        self.table_canvas_window = self.table_canvas.create_window((0, 0), window=self.table_body, anchor="nw")
        
        def _on_table_configure(event):
            self.table_canvas.itemconfig(self.table_canvas_window, width=event.width)
        self.table_canvas.bind("<Configure>", _on_table_configure)

        # Mousewheel support
        def _on_mousewheel(event):
            try:
                if self.table_canvas.winfo_exists():
                    self.table_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except: pass
        self.table_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Pagination Footer
        self.pagination_frame = tk.Frame(container, bg=self.COLORS["bg"], pady=15)
        self.pagination_frame.pack(fill="x")

    def update_table(self):
        if not hasattr(self, 'table_body'): return
        for widget in self.table_body.winfo_children(): widget.destroy()

        query = self.search_var.get().lower().strip()
        display_list = [i for i in self.items_list if query in i['name'].lower()] if query else self.items_list

        total_items = len(display_list)
        total_pages = max(1, (total_items + self.rows_per_page - 1) // self.rows_per_page)
        
        if self.current_page >= total_pages: self.current_page = total_pages - 1
        start = self.current_page * self.rows_per_page
        end = start + self.rows_per_page
        page_data = display_list[start:end]

        for item in page_data:
            r = tk.Frame(self.table_body, bg=self.COLORS["card"], pady=15, padx=25)
            r.pack(fill="x")
            
            for i in range(len(self.weights)):
                r.grid_columnconfigure(i, weight=self.weights[i])

            tk.Label(r, text=item['name'], font=("Segoe UI", 12), bg=self.COLORS["card"], fg="white", anchor="w").grid(row=0, column=0, sticky="ew")
            tk.Label(r, text=f"GH₵ {item['price']:,.2f}", font=("Segoe UI", 12, "bold"), bg=self.COLORS["card"], fg=self.COLORS["success"], anchor="w").grid(row=0, column=1, sticky="ew")
            
            actions = tk.Frame(r, bg=self.COLORS["card"])
            actions.grid(row=0, column=2, sticky="e")
            tk.Button(actions, text="🗑 DELETE", font=("Segoe UI", 9, "bold"), bg=self.COLORS["danger"], fg="white", 
                      bd=0, padx=12, pady=6, cursor="hand2", command=lambda i=item['id']: self.delete_item(i)).pack()
            
            tk.Frame(self.table_body, bg=self.COLORS["border"], height=1).pack(fill="x")

        self.update_pagination_controls(total_pages)
        self.table_body.update_idletasks()
        self.table_canvas.config(scrollregion=self.table_canvas.bbox("all"))

    def update_pagination_controls(self, total_pages):
        for widget in self.pagination_frame.winfo_children(): widget.destroy()
        inner_p = tk.Frame(self.pagination_frame, bg=self.COLORS["bg"])
        inner_p.pack()

        for txt, cmd, active in [("←", self.prev_page, self.current_page > 0), 
                                 (f"{self.current_page + 1} / {total_pages}", None, True), 
                                 ("→", self.next_page, self.current_page < total_pages - 1)]:
            if cmd:
                btn = tk.Button(inner_p, text=txt, font=("Segoe UI", 10, "bold"),
                               fg="white" if active else self.COLORS["text_secondary"],
                               bg=self.COLORS["sidebar"] if active else self.COLORS["bg"],
                               bd=0, padx=15, pady=8, cursor="hand2" if active else "arrow",
                               command=cmd if active else None)
                btn.pack(side="left", padx=10)
            else:
                tk.Label(inner_p, text=txt, font=("Segoe UI", 10), 
                         fg=self.COLORS["text_primary"], bg=self.COLORS["bg"]).pack(side="left", padx=15)

    def prev_page(self):
        self.current_page -= 1
        self.update_table()

    def next_page(self):
        self.current_page += 1
        self.update_table()

    def delete_item(self, iid):
        if messagebox.askyesno("Confirm Delete", "Remove this item from the menu?"):
            if database.delete_inventory_item(iid): 
                self.refresh_data()

    def add_meal_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add New Meal")
        dialog.geometry("400x350")
        dialog.configure(bg=self.COLORS["bg"])
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        main = tk.Frame(dialog, bg=self.COLORS["bg"], padx=30, pady=30)
        main.pack(fill="both", expand=True)

        tk.Label(main, text="Add New Meal", font=("Segoe UI", 18, "bold"), fg="white", bg=self.COLORS["bg"]).pack(pady=(0, 25))

        tk.Label(main, text="Meal Name", fg=self.COLORS["text_secondary"], bg=self.COLORS["bg"]).pack(anchor="w")
        name_entry = tk.Entry(main, font=("Segoe UI", 11), bg=self.COLORS["card"], fg="white", borderwidth=0)
        name_entry.pack(fill="x", pady=(5, 20), ipady=10)

        tk.Label(main, text="Price (GH₵)", fg=self.COLORS["text_secondary"], bg=self.COLORS["bg"]).pack(anchor="w")
        price_entry = tk.Entry(main, font=("Segoe UI", 11), bg=self.COLORS["card"], fg="white", borderwidth=0)
        price_entry.pack(fill="x", pady=(5, 20), ipady=10)

        def save():
            try:
                n = name_entry.get().strip()
                p = float(price_entry.get().replace('GH₵', '').strip())
                if not n: throw
                if database.add_inventory_item(n, "Meal", p):
                    self.refresh_data()
                    dialog.destroy()
                    messagebox.showinfo("Success", f"'{n}' added to menu.")
            except: messagebox.showwarning("Error", "Please enter a valid meal name and price.")

        tk.Button(main, text="Save Meal", font=("Segoe UI", 12, "bold"), bg=self.COLORS["accent"], fg="white", 
                  bd=0, pady=12, cursor="hand2", command=save).pack(fill="x", pady=(10, 0))
