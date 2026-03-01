# Redesigned Professional Rooms Page
import tkinter as tk
from tkinter import ttk, messagebox
import database

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
            "warning": "#F59E0B",
            "danger": "#EF4444"
        }
        super().__init__(parent, bg=self.COLORS["bg"])
        
        self.rooms_list_frame = None
        self.pagination_frame = None
        self.rooms_data = database.get_rooms()
        self.display_data = list(self.rooms_data)
        self.search_var = tk.StringVar()
        
        # Pagination
        self.current_page = 0
        self.rows_per_page = 10
        self.weights = [15, 20, 15, 15, 20]
        self.cols = ["Room Number", "Type", "Status", "Price", "Actions"]
        
        self.create_widgets()
        self.update_rooms_list()
        
        # Unbind mousewheel when destroyed
        self.bind("<Destroy>", self.on_destroy)

    def on_destroy(self, event):
        if event.widget == self:
            try:
                self.unbind_all("<MouseWheel>")
            except: pass

    def create_widgets(self):
        # Header with Search/Actions
        header = tk.Frame(self, bg=self.COLORS["bg"], pady=20)
        header.pack(fill="x")

        # Search Bar
        search_container = tk.Frame(header, bg=self.COLORS["card"], 
                                    padx=15, pady=8, highlightbackground=self.COLORS["border"], highlightthickness=1)
        search_container.pack(side="left")
        
        tk.Label(search_container, text="🔍", bg=self.COLORS["card"], fg=self.COLORS["text_secondary"]).pack(side="left")
        search_entry = tk.Entry(search_container, textvariable=self.search_var, bg=self.COLORS["card"], fg=self.COLORS["text_primary"], 
                                 insertbackground="white", border=0, font=("Segoe UI", 11), width=40)
        search_entry.pack(side="left", padx=10)
        
        def on_search_focus_in(e):
            if self.search_var.get() == "Search rooms...":
                self.search_var.set("")
        def on_search_focus_out(e):
            if not self.search_var.get():
                self.search_var.set("Search rooms...")
        
        search_entry.bind("<FocusIn>", on_search_focus_in)
        search_entry.bind("<FocusOut>", on_search_focus_out)
        self.search_var.set("Search rooms...")
        self.search_var.trace_add("write", lambda *args: self.search_rooms(self.search_var.get()))

        # Add Room Button
        add_btn = tk.Button(header, text="+ Add New Room", font=("Segoe UI", 11, "bold"),
                           fg="white", bg=self.COLORS["accent"], activebackground="#4F46E5",
                           activeforeground="white", bd=0, relief="flat", padx=20, pady=8, cursor="hand2",
                           command=self.add_room_dialog)
        add_btn.pack(side="right")

        # Main Table Container
        main_container = tk.Frame(self, bg=self.COLORS["card"], 
                                  highlightbackground=self.COLORS["border"], highlightthickness=1)
        # Added side padding of 60 to prevent the table from being too wide
        main_container.pack(fill="both", expand=True, padx=60, pady=(0, 20))

        # Structural fix for exact column alignment: Header and Canvas share inner_container
        # Scrollbar is outside inner_container
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=None)
        scrollbar.pack(side="right", fill="y")
        
        inner_container = tk.Frame(main_container, bg=self.COLORS["card"])
        inner_container.pack(side="left", fill="both", expand=True)

        # Table Header (Inside inner_container)
        table_header = tk.Frame(inner_container, bg=self.COLORS["sidebar"], pady=15, padx=20)
        table_header.pack(fill="x")
        
        for i, col in enumerate(self.cols):
            lbl = tk.Label(table_header, text=col.upper(), font=("Segoe UI", 10, "bold"),
                           fg=self.COLORS["accent"], bg=self.COLORS["sidebar"])
            lbl.grid(row=0, column=i, sticky="ew")
            table_header.grid_columnconfigure(i, weight=self.weights[i])

        # Canvas (Inside inner_container)
        canvas = tk.Canvas(inner_container, bg=self.COLORS["card"], highlightthickness=0, height=500)
        canvas.pack(fill="both", expand=True)
        
        scrollbar.config(command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        self.rooms_list_frame = tk.Frame(canvas, bg=self.COLORS["card"])
        canvas.create_window((0, 0), window=self.rooms_list_frame, anchor="nw")
        
        def _on_canvas_configure(event):
            canvas.itemconfig(canvas.find_all()[0], width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Mousewheel Support
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except: pass
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Pagination Footer
        self.pagination_frame = tk.Frame(self, bg=self.COLORS["bg"], pady=10)
        self.pagination_frame.pack(fill="x", side="bottom")

    def update_rooms_list(self):
        if not self.rooms_list_frame: return
        for widget in self.rooms_list_frame.winfo_children(): widget.destroy()

        self.rooms_data = database.get_rooms()
        self.search_rooms(self.search_var.get())

    def search_rooms(self, query):
        if not self.rooms_list_frame: return
        query = query.lower().strip()
        if not query or query == "search rooms...":
            self.display_data = list(self.rooms_data)
        else:
            self.display_data = [r for r in self.rooms_data if query in str(r["room_number"]).lower() or query in r["type"].lower() or query in r["status"].lower()]
        
        # 1. Pagination Slice
        total_items = len(self.display_data)
        total_pages = max(1, (total_items + self.rows_per_page - 1) // self.rows_per_page)
        
        if self.current_page >= total_pages: self.current_page = total_pages - 1
        start = self.current_page * self.rows_per_page
        end = start + self.rows_per_page
        page_data = self.display_data[start:end]

        # 2. Render Page Rows
        for idx, room in enumerate(page_data):
            num, r_type, status, price = room["room_number"], room["type"], room["status"], room["price"]
            
            row = tk.Frame(self.rooms_list_frame, bg=self.COLORS["card"], pady=12, padx=20)
            row.pack(fill="x")
            
            for i in range(len(self.weights)):
                row.grid_columnconfigure(i, weight=self.weights[i])

            # Column 0: Room Number
            tk.Label(row, text=str(num), font=("Segoe UI", 11), fg=self.COLORS["text_primary"], 
                     bg=self.COLORS["card"], anchor="w").grid(row=0, column=0, sticky="ew")
            
            # Column 1: Type
            tk.Label(row, text=r_type, font=("Segoe UI", 11), fg=self.COLORS["text_secondary"], 
                     bg=self.COLORS["card"], anchor="w").grid(row=0, column=1, sticky="ew")

            # Column 2: Status Badge
            color = self.COLORS["success"] if status == "Available" else (self.COLORS["danger"] if status == "Occupied" else self.COLORS["warning"])
            badge_container = tk.Frame(row, bg=self.COLORS["card"])
            badge_container.grid(row=0, column=2, sticky="ew")
            badge_bg = tk.Frame(badge_container, bg=color, padx=12, pady=4)
            badge_bg.pack()
            tk.Label(badge_bg, text=status.upper(), font=("Segoe UI", 9, "bold"), fg="white", bg=color).pack()

            # Column 3: Price
            display_price = str(price).replace('$', 'GH₵ ')
            tk.Label(row, text=display_price, font=("Segoe UI", 11, "bold"), fg=self.COLORS["text_primary"], 
                     bg=self.COLORS["card"], anchor="e").grid(row=0, column=3, sticky="ew", padx=(0, 15))

            # Column 4: Actions
            actions_frame = tk.Frame(row, bg=self.COLORS["card"])
            actions_frame.grid(row=0, column=4, sticky="ew")
            inner_actions = tk.Frame(actions_frame, bg=self.COLORS["card"])
            inner_actions.pack()
            
            tk.Button(inner_actions, text="✏", font=("Segoe UI", 12), bg=self.COLORS["card"], 
                      fg=self.COLORS["accent"], bd=0, cursor="hand2", 
                      command=lambda r=room: self.add_room_dialog(edit_data=r)).pack(side="left", padx=10)
            
            tk.Button(inner_actions, text="DELETE", font=("Segoe UI", 9, "bold"), bg=self.COLORS["danger"], 
                      fg="white", bd=0, padx=12, pady=4, cursor="hand2", 
                      command=lambda n=num: self.delete_room_confirm(n)).pack(side="left", padx=5)

            # Row border bottom
            tk.Frame(self.rooms_list_frame, bg=self.COLORS["border"], height=1).pack(fill="x")

        # 3. Update Pagination Controls
        self.update_pagination_controls(total_pages)

    def update_pagination_controls(self, total_pages):
        for widget in self.pagination_frame.winfo_children(): widget.destroy()
        
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
            self.update_rooms_list()

    def next_page(self):
        total_items = len(self.display_data)
        total_pages = (total_items + self.rows_per_page - 1) // self.rows_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_rooms_list()

    def delete_room_confirm(self, room_number):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Room {room_number}?"):
            if database.delete_room(room_number):
                self.update_rooms_list()
                messagebox.showinfo("Success", "Room deleted successfully.")
            else:
                messagebox.showerror("Error", "Could not delete room.")

    def add_room_dialog(self, edit_data=None):
        title = "Edit Room" if edit_data else "Add New Room"
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("440x600")
        dialog.configure(bg=self.COLORS["bg"])
        
        main_frame = tk.Frame(dialog, bg=self.COLORS["bg"], padx=30, pady=30)
        main_frame.pack(fill="both", expand=True)
        
        tk.Label(main_frame, text="Room Details", font=("Segoe UI", 18, "bold"), 
                 fg="white", bg=self.COLORS["bg"]).pack(pady=(0, 20))
        
        fields = ["Room Number", "Room Type", "Status", "Price (GH₵)"]
        entries = {}
        
        for f in fields:
            tk.Label(main_frame, text=f, font=("Segoe UI", 10), 
                     fg=self.COLORS["text_secondary"], bg=self.COLORS["bg"]).pack(anchor="w")
            
            if f == "Status":
                entry = ttk.Combobox(main_frame, values=["Available", "Occupied", "Maintenance"], 
                                     font=("Segoe UI", 11), state="readonly")
                entry.current(0)
                if edit_data: entry.set(edit_data["status"])
            elif f == "Room Type":
                entry = ttk.Combobox(main_frame, values=["Single", "Double", "Suite", "Deluxe"], 
                                     font=("Segoe UI", 11), state="readonly")
                entry.current(0)
                if edit_data: entry.set(edit_data["type"])
            else:
                entry = tk.Entry(main_frame, bg=self.COLORS["card"], fg="white", 
                                 insertbackground="white", borderwidth=1, relief="flat", font=("Segoe UI", 11))
                if edit_data:
                    val = edit_data["room_number"] if f == "Room Number" else edit_data["price"]
                    entry.insert(0, str(val).replace('GH₵ ', '').strip())
            
            entry.pack(fill="x", pady=(5, 15), ipady=5)
            entries[f] = entry
            
        def save():
            num = entries["Room Number"].get()
            rtype = entries["Room Type"].get()
            stat = entries["Status"].get()
            price = entries["Price (GH₵)"].get()
            
            if not num or not price: 
                messagebox.showwarning("Warning", "All fields are required.")
                return
            
            formatted_price = f"GH₵ {price.replace('GH₵', '').strip()}"
            
            if edit_data:
                success = database.update_room(num, rtype, stat, formatted_price, old_number=edit_data["room_number"])
            else:
                success = database.add_room(num, rtype, stat, formatted_price)
            
            if success:
                self.update_rooms_list()
                dialog.destroy()
                msg = "Room updated successfully." if edit_data else "Room added successfully."
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Error", "Operation failed. Room number might already exist.")
            
        btn_text = "Update Room" if edit_data else "Save Room"
        tk.Button(main_frame, text=btn_text, font=("Segoe UI", 12, "bold"),
                  fg="white", bg=self.COLORS["accent"], activebackground="#4F46E5",
                  activeforeground="white", bd=0, relief="flat", pady=10, cursor="hand2",
                  command=save).pack(fill="x", pady=(10, 0))

if __name__ == "__main__":
    root = tk.Tk()
    page = RoomsPage(root)
    page.pack(fill="both", expand=True)
    root.mainloop()
