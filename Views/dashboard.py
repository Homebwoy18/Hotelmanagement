

# Redesigned Professional Dashboard
import tkinter as tk
from tkinter import ttk
from Views.reservation import ReservationPage
from Views.rooms import RoomsPage
from Views.inventory import InventoryPage
from Views.report import ReportPage

class DashboardWindow(tk.Toplevel):
    # Professional Color Palette
    COLORS = {
        "bg": "#111827",          # Deep Slate
        "sidebar": "#1F2937",     # Dark Gray
        "card": "#1F2937",
        "accent": "#6366F1",      # Indigo
        "text_primary": "#F9FAFB",
        "text_secondary": "#9CA3AF",
        "border": "#374151"
    }

    def __init__(self, master=None):
        super().__init__(master)
        self.title("HotelEase Management")
        self.geometry("1400x900")
        self.configure(bg=self.COLORS["bg"])
        self.resizable(True, True)
        
        self.active_page = "Dashboard"
        self.sidebar_buttons = {}
        self.sidebar = None
        self.content_area = None
        self.topbar = None
        self.page_title = None
        self.main = None
        
        # State data (mock)
        self.all_data = [
            ("John Doe", "101", "2026-02-27", "2026-03-01", "Confirmed"),
            ("Jane Smith", "205", "2026-02-28", "2026-03-03", "Checked-in"),
            ("Alice Brown", "303", "2026-03-01", "2026-03-05", "Pending"),
            ("Bob Lee", "104", "2026-03-02", "2026-03-06", "Confirmed"),
            ("Chris Kim", "110", "2026-03-03", "2026-03-07", "Checked-in"),
            ("Dana Fox", "120", "2026-03-04", "2026-03-08", "Pending"),
            ("Eve Lin", "130", "2026-03-05", "2026-03-09", "Confirmed"),
            ("Frank Wu", "140", "2026-03-06", "2026-03-10", "Checked-in"),
            ("Grace Yu", "150", "2026-03-07", "2026-03-11", "Pending"),
            ("Helen Z", "160", "2026-03-08", "2026-03-12", "Confirmed"),
        ]
        self.current_page = 1
        self.rows_per_page = 8

        self.setup_styles()
        self.create_layout()
        self.show_dashboard()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Treeview styling
        style.configure("Treeview", 
                        background=self.COLORS["card"],
                        foreground=self.COLORS["text_primary"],
                        rowheight=45,
                        fieldbackground=self.COLORS["card"],
                        borderwidth=0,
                        font=("Segoe UI", 10))
        
        style.configure("Treeview.Heading", 
                        background=self.COLORS["sidebar"],
                        foreground=self.COLORS["accent"],
                        font=("Segoe UI", 11, "bold"),
                        borderwidth=0)
        
        style.map("Treeview", 
                  background=[("selected", self.COLORS["accent"])],
                  foreground=[("selected", "white")])

    def create_layout(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=self.COLORS["sidebar"], width=260)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Sidebar Header
        logo_frame = tk.Frame(self.sidebar, bg=self.COLORS["sidebar"], pady=40)
        logo_frame.pack(fill="x")
        logo = tk.Label(logo_frame, text="HotelEase", font=("Segoe UI", 24, "bold"), 
                        fg=self.COLORS["accent"], bg=self.COLORS["sidebar"])
        logo.pack()

        # Navigation
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Reservation", self.show_reservation),
            ("Rooms", self.show_rooms),
            ("Inventory", self.show_inventory),
            ("Report", self.show_report),
            ("Logout", self.logout)
        ]
        
        for name, cmd in nav_items:
            btn = tk.Label(self.sidebar, text=f"   {name}", font=("Segoe UI", 12, "bold"),
                          fg=self.COLORS["text_secondary"], bg=self.COLORS["sidebar"],
                          padx=30, pady=15, anchor="w", cursor="hand2")
            btn.pack(fill="x", pady=2)
            btn.bind("<Button-1>", lambda e, c=cmd: c())
            btn.bind("<Enter>", lambda e, b=btn, n=name: self.on_nav_enter(b, n))
            btn.bind("<Leave>", lambda e, b=btn, n=name: self.on_nav_leave(b, n))
            self.sidebar_buttons[name] = btn

        # Main Area
        self.content_area = tk.Frame(self, bg=self.COLORS["bg"])
        self.content_area.pack(side="right", fill="both", expand=True)

        # Top Bar
        self.topbar = tk.Frame(self.content_area, bg=self.COLORS["bg"], height=80)
        self.topbar.pack(side="top", fill="x", padx=40, pady=20)
        self.topbar.pack_propagate(False)

        self.page_title = tk.Label(self.topbar, text="Overview", font=("Segoe UI", 24, "bold"), 
                                  fg=self.COLORS["text_primary"], bg=self.COLORS["bg"])
        self.page_title.pack(side="left")

        # Profile
        profile_frame = tk.Frame(self.topbar, bg=self.COLORS["bg"])
        profile_frame.pack(side="right")
        tk.Label(profile_frame, text="Admin", font=("Segoe UI", 12, "bold"), 
                 fg=self.COLORS["text_primary"], bg=self.COLORS["bg"]).pack(side="right", padx=10)
        # Simple Circle Avatar
        avatar = tk.Canvas(profile_frame, width=40, height=40, bg=self.COLORS["bg"], highlightthickness=0)
        avatar.create_oval(2, 2, 38, 38, fill=self.COLORS["accent"], outline="")
        avatar.pack(side="right")

        # Main Page Container
        self.main = tk.Frame(self.content_area, bg=self.COLORS["bg"])
        self.main.pack(fill="both", expand=True, padx=40, pady=(0, 40))

    def on_nav_enter(self, btn, name):
        if self.active_page != name:
            btn.config(bg="#374151", fg="white")

    def on_nav_leave(self, btn, name):
        if self.active_page != name:
            btn.config(bg=self.COLORS["sidebar"], fg=self.COLORS["text_secondary"])
        else:
            btn.config(bg=self.COLORS["accent"], fg="white")

    def set_active_nav(self, nav_name):
        self.active_page = nav_name
        self.page_title.config(text=nav_name)
        for name, btn in self.sidebar_buttons.items():
            if name == nav_name:
                btn.config(bg=self.COLORS["accent"], fg="white")
            else:
                btn.config(bg=self.COLORS["sidebar"], fg=self.COLORS["text_secondary"])

    def clear_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def create_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=self.COLORS["card"], padx=25, pady=25,
                        highlightbackground=self.COLORS["border"], highlightthickness=1)
        tk.Label(card, text=title, font=("Segoe UI", 11), fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 28, "bold"), fg=color, bg=self.COLORS["card"]).pack(anchor="w", pady=(5, 0))
        return card

    def show_dashboard(self):
        self.clear_main()
        self.set_active_nav("Dashboard")
        
        # Summary Cards
        cards_container = tk.Frame(self.main, bg=self.COLORS["bg"])
        cards_container.pack(fill="x", pady=(0, 30))
        cards_container.grid_columnconfigure((0, 1, 2, 3), weight=1)

        summary = [
            ("Total Bookings", "1,280", self.COLORS["accent"]),
            ("Rooms Available", "45", "#10B981"), # Emerald
            ("Check-Outs Today", "12", "#F59E0B"), # Amber
            ("Total Revenue", "$12,450", "#EC4899") # Pink
        ]

        for i, (t, v, c) in enumerate(summary):
            card = self.create_card(cards_container, t, v, c)
            card.grid(row=0, column=i, padx=(0 if i == 0 else 10, 0), sticky="ew")

        # Table Section
        table_container = tk.Frame(self.main, bg=self.COLORS["card"], 
                                   highlightbackground=self.COLORS["border"], highlightthickness=1)
        table_container.pack(fill="both", expand=True)

        header_frame = tk.Frame(table_container, bg=self.COLORS["card"], pady=20, padx=20)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Recent Bookings", font=("Segoe UI", 14, "bold"), 
                 fg=self.COLORS["text_primary"], bg=self.COLORS["card"]).pack(side="left")

        columns = ("Guest Name", "Room", "Check-in", "Check-out", "Status")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.update_table()

    def update_table(self):
        # Clear current rows
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        start = (self.current_page - 1) * self.rows_per_page
        end = start + self.rows_per_page
        
        for row in self.all_data[start:end]:
            self.tree.insert("", "end", values=row)

    def show_reservation(self):
        self.clear_main()
        self.set_active_nav("Reservation")
        page = ReservationPage(self.main)
        page.pack(fill="both", expand=True)

    def show_rooms(self):
        self.clear_main()
        self.set_active_nav("Rooms")
        page = RoomsPage(self.main)
        page.pack(fill="both", expand=True)

    def show_inventory(self):
        self.clear_main()
        self.set_active_nav("Inventory")
        page = InventoryPage(self.main)
        page.pack(fill="both", expand=True)

    def show_report(self):
        self.clear_main()
        self.set_active_nav("Report")
        page = ReportPage(self.main)
        page.pack(fill="both", expand=True)

    def logout(self):
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    dash = DashboardWindow(master=root)
    dash.mainloop()
