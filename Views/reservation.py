
# Modern Reservation Page
import tkinter as tk
from tkinter import ttk
from tkinter import Canvas, Frame, Scrollbar

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
            "warning": "#F59E0B"
        }
        super().__init__(parent, bg=self.COLORS["bg"])

        # --- Scrollable Canvas Setup ---
        self.canvas = Canvas(self, bg=self.COLORS["bg"], highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        vscroll = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        vscroll.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=vscroll.set)
        
        self.inner = Frame(self.canvas, bg=self.COLORS["bg"])
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.setup_ui()
        
        # Mousewheel scroll support
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def setup_ui(self):
        # Title
        title = tk.Label(self.inner, text="RESERVATIONS", font=("Segoe UI", 18, "bold"), 
                         bg=self.COLORS["bg"], fg=self.COLORS["accent"])
        title.pack(anchor="w", padx=40, pady=(30, 10))

        # Form Container (Card)
        form_card = tk.Frame(self.inner, bg=self.COLORS["card"], 
                             highlightbackground=self.COLORS["border"], highlightthickness=1)
        form_card.pack(fill="x", padx=40, pady=20)
        
        form_inner = tk.Frame(form_card, bg=self.COLORS["card"], padx=30, pady=30)
        form_inner.pack(fill="x")

        # Field Labels and Entries
        self.entries = {}
        fields = [
            ("Customer Name", 0, 0), ("Gender", 0, 1), ("Phone Number", 0, 2),
            ("Number of Days", 1, 0), ("Room", 1, 1), ("Check-in Date", 1, 2), ("Check-out Date", 1, 3)
        ]

        from tkcalendar import DateEntry
        
        for name, r, c in fields:
            f_container = tk.Frame(form_inner, bg=self.COLORS["card"])
            f_container.grid(row=r, column=c, padx=10, pady=10, sticky="ew")
            
            tk.Label(f_container, text=name, font=("Segoe UI", 10, "bold"), 
                     fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).pack(anchor="w")
            
            if name == "Gender":
                entry = ttk.Combobox(f_container, values=["Male", "Female", "Other"], font=("Segoe UI", 11), state="readonly")
                entry.current(0)
            elif name == "Room":
                entry = ttk.Combobox(f_container, values=["101", "102", "103", "104", "201", "202"], font=("Segoe UI", 11), state="readonly")
                entry.current(0)
            elif "Date" in name:
                entry = DateEntry(f_container, font=("Segoe UI", 11), background=self.COLORS["accent"], foreground="white", borderwidth=0)
            else:
                entry = tk.Entry(f_container, font=("Segoe UI", 11), bg=self.COLORS["bg"], fg=self.COLORS["text_primary"], 
                                 insertbackground="white", relief="flat", highlightbackground=self.COLORS["border"], highlightthickness=1)
            
            entry.pack(fill="x", pady=(5, 0), ipady=2)
            self.entries[name] = entry

        for i in range(4): form_inner.grid_columnconfigure(i, weight=1)

        # Action Button
        btn_container = tk.Frame(form_inner, bg=self.COLORS["accent"], padx=25, pady=10)
        btn_container.grid(row=2, column=0, columnspan=4, pady=(20, 0))
        add_btn = tk.Label(btn_container, text="Add Reservation", font=("Segoe UI", 11, "bold"), 
                           fg="white", bg=self.COLORS["accent"], cursor="hand2")
        add_btn.pack()

        # Table Container (Card)
        table_card = tk.Frame(self.inner, bg=self.COLORS["card"], 
                              highlightbackground=self.COLORS["border"], highlightthickness=1)
        table_card.pack(fill="both", expand=True, padx=40, pady=(20, 40))

        # Table Header
        header_cols = ["Guest Name", "Room", "Check-in", "Check-out", "Status"]
        table_header = tk.Frame(table_card, bg=self.COLORS["sidebar"], pady=15)
        table_header.pack(fill="x")
        
        for i, col in enumerate(header_cols):
            lbl = tk.Label(table_header, text=col.upper(), font=("Segoe UI", 10, "bold"),
                           fg=self.COLORS["accent"], bg=self.COLORS["sidebar"])
            lbl.grid(row=0, column=i, sticky="ew")
            table_header.grid_columnconfigure(i, weight=1)

        self.table_body = tk.Frame(table_card, bg=self.COLORS["card"])
        self.table_body.pack(fill="both", expand=True)

        self.all_data = [
            ("John Doe", "101", "2026-02-27", "2026-03-01", "Confirmed"),
            ("Jane Smith", "205", "2026-02-28", "2026-03-03", "Checked-in"),
            ("Alice Brown", "303", "2026-03-01", "2026-03-05", "Pending"),
            ("Bob Lee", "104", "2026-03-02", "2026-03-06", "Confirmed"),
            ("Chris Kim", "110", "2026-03-03", "2026-03-07", "Checked-in"),
        ]
        
        self.update_table()

    def update_table(self):
        for widget in self.table_body.winfo_children(): widget.destroy()
        
        for row_data in self.all_data:
            row = tk.Frame(self.table_body, bg=self.COLORS["card"], pady=12)
            row.pack(fill="x")
            tk.Frame(self.table_body, bg=self.COLORS["border"], height=1).pack(fill="x")

            for i, val in enumerate(row_data):
                row.grid_columnconfigure(i, weight=1)
                if i == 4: # Status Badge
                    color = self.COLORS["success"] if val == "Confirmed" or val == "Checked-in" else self.COLORS["warning"]
                    b_bg = tk.Frame(row, bg=color, padx=12, pady=4)
                    b_bg.grid(row=0, column=i)
                    tk.Label(b_bg, text=val.upper(), font=("Segoe UI", 9, "bold"), fg="white", bg=color).pack()
                else:
                    tk.Label(row, text=val, font=("Segoe UI", 11), fg=self.COLORS["text_primary"], bg=self.COLORS["card"]).grid(row=0, column=i)

    def _on_mousewheel(self, event):
        try: self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except: pass

    def destroy(self):
        try: self.canvas.unbind_all("<MouseWheel>")
        except: pass
        super().destroy()
