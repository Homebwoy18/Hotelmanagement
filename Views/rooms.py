# Redesigned Professional Rooms Page
import tkinter as tk
from tkinter import ttk, messagebox
import database
from Views.theme import COLORS

class RoomsPage(tk.Frame):
    def __init__(self, parent):
        self.COLORS = COLORS
        self._status_filter = None  # None = show all
        super().__init__(parent, bg=COLORS["bg"])
        
        self.rooms_list_frame = None
        self.pagination_frame = None
        self._canvas = None  # stored so scroll region can be updated after render
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
        header = tk.Frame(self, bg=COLORS["bg"], pady=20)
        header.pack(fill="x")

        # Search Bar
        search_container = tk.Frame(header, bg=COLORS["card"],
                                    padx=15, pady=8,
                                    highlightbackground=COLORS["border"], highlightthickness=1)
        search_container.pack(side="left")
        tk.Label(search_container, text="🔍", bg=COLORS["card"], fg=COLORS["text_secondary"]).pack(side="left")
        search_entry = tk.Entry(search_container, textvariable=self.search_var, bg=COLORS["card"],
                                fg=COLORS["text_primary"], insertbackground="white",
                                border=0, font=("Segoe UI", 11), width=30)
        search_entry.pack(side="left", padx=10)
        self.search_var.trace_add("write", lambda *args: self.search_rooms(self.search_var.get()))

        # Status filter buttons
        filter_frame = tk.Frame(header, bg=COLORS["bg"])
        filter_frame.pack(side="left", padx=20)
        for label, val in [("All", None), ("Available", "Available"),
                           ("Occupied", "Occupied"), ("Maintenance", "Maintenance")]:
            tk.Button(
                filter_frame, text=label, font=("Segoe UI", 9, "bold"),
                fg="white", bg=COLORS["sidebar"], activebackground=COLORS["accent"],
                activeforeground="white", bd=0, padx=12, pady=6, cursor="hand2",
                command=lambda v=val: self._apply_filter(v)
            ).pack(side="left", padx=3)

        # Add Room Button
        add_btn = tk.Button(header, text="+ Add New Room", font=("Segoe UI", 11, "bold"),
                            fg="white", bg=COLORS["accent"], activebackground=COLORS["accent_hover"],
                            activeforeground="white", bd=0, relief="flat", padx=20, pady=8,
                            cursor="hand2", command=self.add_room_dialog)
        add_btn.pack(side="right")

        # Main Table Container
        main_container = tk.Frame(self, bg=self.COLORS["card"],
                                  highlightbackground=self.COLORS["border"], highlightthickness=1)
        main_container.pack(fill="both", expand=True, padx=60, pady=(0, 20))

        inner_container = tk.Frame(main_container, bg=self.COLORS["card"])
        inner_container.pack(side="left", fill="both", expand=True)

        # Table Header
        table_header = tk.Frame(inner_container, bg=self.COLORS["sidebar"], pady=15, padx=20)
        table_header.pack(fill="x")
        for i, col in enumerate(self.cols):
            lbl = tk.Label(table_header, text=col.upper(), font=("Segoe UI", 10, "bold"),
                           fg=self.COLORS["accent"], bg=self.COLORS["sidebar"])
            lbl.grid(row=0, column=i, sticky="ew")
            table_header.grid_columnconfigure(i, weight=self.weights[i])

        # Scrollable canvas
        scrollbar = ttk.Scrollbar(main_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self._canvas = tk.Canvas(inner_container, bg=self.COLORS["card"],
                                 highlightthickness=0, height=500,
                                 yscrollcommand=scrollbar.set)
        self._canvas.pack(fill="both", expand=True)
        scrollbar.config(command=self._canvas.yview)

        self.rooms_list_frame = tk.Frame(self._canvas, bg=self.COLORS["card"])
        self._canvas_window = self._canvas.create_window((0, 0), window=self.rooms_list_frame, anchor="nw")

        # Keep inner frame width matched to canvas width
        def _on_canvas_resize(event):
            self._canvas.itemconfig(self._canvas_window, width=event.width)
        self._canvas.bind("<Configure>", _on_canvas_resize)

        # Mousewheel support
        def _on_mousewheel(event):
            try:
                if self._canvas and self._canvas.winfo_exists():
                    self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass
        self._canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Pagination Footer
        self.pagination_frame = tk.Frame(self, bg=self.COLORS["bg"], pady=10)
        self.pagination_frame.pack(fill="x", side="bottom")

    def _apply_filter(self, status_value):
        self._status_filter = status_value
        self.current_page = 0
        self.update_rooms_list()

    def update_rooms_list(self):
        if not self.rooms_list_frame: return
        for widget in self.rooms_list_frame.winfo_children(): widget.destroy()

        self.rooms_data = database.get_rooms()
        # Apply status filter before search
        if self._status_filter:
            self.rooms_data = [r for r in self.rooms_data if r["status"] == self._status_filter]
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

            # Column 3: Price — strip currency symbols/commas before parsing
            try:
                price_str = str(price).replace("GH₵", "").replace(",", "").strip()
                display_price = f"GH₵ {float(price_str):,.2f}" if price_str else "N/A"
            except (ValueError, TypeError):
                display_price = str(price) if price else "N/A"
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

        # 3. Update scroll region so the scrollbar knows the full content height
        self.rooms_list_frame.update_idletasks()
        if self._canvas:
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))

        # 4. Update Pagination Controls
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

            try:
                formatted_price = float(price.replace('GH₵', '').replace(',', '').strip())
            except ValueError:
                messagebox.showwarning("Warning", "Price must be a valid number (e.g. 250 or 1500.00).")
                return

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
