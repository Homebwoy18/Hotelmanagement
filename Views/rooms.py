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
        self.rooms_data = database.get_rooms()
        self.create_widgets()
        self.update_rooms_list()

    def create_widgets(self):
        # Header with Search/Actions
        header = tk.Frame(self, bg=self.COLORS["bg"], pady=20)
        header.pack(fill="x")

        # Search Bar
        search_container = tk.Frame(header, bg=self.COLORS["card"], 
                                    padx=15, pady=8, highlightbackground=self.COLORS["border"], highlightthickness=1)
        search_container.pack(side="left")
        
        tk.Label(search_container, text="🔍", bg=self.COLORS["card"], fg=self.COLORS["text_secondary"]).pack(side="left")
        search_entry = tk.Entry(search_container, bg=self.COLORS["card"], fg=self.COLORS["text_primary"], 
                                 insertbackground="white", border=0, font=("Segoe UI", 11), width=40)
        search_entry.pack(side="left", padx=10)
        search_entry.insert(0, "Search rooms...")

        # Add Room Button
        add_btn = tk.Button(header, text="+ Add New Room", font=("Segoe UI", 11, "bold"),
                           fg="white", bg=self.COLORS["accent"], activebackground="#4F46E5",
                           activeforeground="white", bd=0, relief="flat", padx=20, pady=8, cursor="hand2",
                           command=self.add_room_dialog)
        add_btn.pack(side="right")

        # Main Table Container
        main_container = tk.Frame(self, bg=self.COLORS["card"], 
                                  highlightbackground=self.COLORS["border"], highlightthickness=1)
        main_container.pack(fill="both", expand=True)

        # Table Header
        table_header = tk.Frame(main_container, bg=self.COLORS["sidebar"], pady=15)
        table_header.pack(fill="x")
        
        cols = ["Room Number", "Type", "Status", "Price", "Actions"]
        for i, col in enumerate(cols):
            lbl = tk.Label(table_header, text=col.upper(), font=("Segoe UI", 10, "bold"),
                           fg=self.COLORS["accent"], bg=self.COLORS["sidebar"])
            lbl.grid(row=0, column=i, sticky="ew")
            table_header.grid_columnconfigure(i, weight=1)

        self.rooms_list_frame = tk.Frame(main_container, bg=self.COLORS["card"])
        self.rooms_list_frame.pack(fill="both", expand=True)

    def update_rooms_list(self):
        # Clear existing rows
        for widget in self.rooms_list_frame.winfo_children():
            widget.destroy()

        self.rooms_data = database.get_rooms()
        
        for idx, room in enumerate(self.rooms_data):
            num, r_type, status, price = room["room_number"], room["type"], room["status"], room["price"]
            
            row = tk.Frame(self.rooms_list_frame, bg=self.COLORS["card"], pady=12)
            row.pack(fill="x")
            
            # Row border bottom
            sep = tk.Frame(self.rooms_list_frame, bg=self.COLORS["border"], height=1)
            sep.pack(fill="x")

            for i, val in enumerate([num, r_type, status, price, "actions"]):
                row.grid_columnconfigure(i, weight=1)
                
                if i == 2: # Status Badge
                    color = self.COLORS["success"] if val == "Available" else (self.COLORS["danger"] if val == "Occupied" else self.COLORS["warning"])
                    badge_bg = tk.Frame(row, bg=color, padx=12, pady=4)
                    badge_bg.grid(row=0, column=i)
                    tk.Label(badge_bg, text=val.upper(), font=("Segoe UI", 9, "bold"), fg="white", bg=color).pack()
                
                elif i == 4: # Actions
                    actions_frame = tk.Frame(row, bg=self.COLORS["card"])
                    actions_frame.grid(row=0, column=i)
                    
                    tk.Button(actions_frame, text="✏", font=("Segoe UI", 12), bg=self.COLORS["card"], 
                              fg=self.COLORS["accent"], bd=0, cursor="hand2", 
                              command=lambda r=room: self.add_room_dialog(edit_data=r)).pack(side="left", padx=10)
                    
                    # Highlighted Delete Button
                    tk.Button(actions_frame, text="DELETE", font=("Segoe UI", 9, "bold"), bg=self.COLORS["danger"], 
                              fg="white", bd=0, padx=12, pady=4, cursor="hand2", 
                              command=lambda n=num: self.delete_room_confirm(n)).pack(side="left", padx=5)
                
                else:
                    display_val = str(val).replace('$', 'GH₵ ')
                    tk.Label(row, text=display_val, font=("Segoe UI", 11), fg=self.COLORS["text_primary"], 
                             bg=self.COLORS["card"]).grid(row=0, column=i)

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
