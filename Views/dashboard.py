# Redesigned Professional Dashboard
import tkinter as tk
from tkinter import ttk, messagebox
from Views.rooms import RoomsPage
from Views.reservation import ReservationPage
from Views.history import HistoryPage
from Views.inventory import InventoryPage
import database

class DashboardWindow(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.COLORS = {
            "bg": "#111827",
            "sidebar": "#1F2937",
            "card": "#1F2937",
            "accent": "#6366F1",
            "text_primary": "#F9FAFB",
            "text_secondary": "#9CA3AF",
            "border": "#374151"
        }
        
        self.master.title("Hotel Management - Dashboard")
        self.master.geometry("1400x900")
        self.pack(fill="both", expand=True)

        self.all_data = []
        self.table_body = None
        
        self.active_page = "Dashboard"
        self.sidebar_buttons = {} 
        self.sidebar = None
        self.content_area = None
        self.topbar = None
        self.page_title = None
        self.main = None

        self.setup_styles()
        self.create_layout()
        
        # Navigation initialized in create_layout/sidebar section or after
        self.show_dashboard()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=self.COLORS["card"], foreground="white", fieldbackground=self.COLORS["card"], borderwidth=0)
        style.map("Treeview", background=[('selected', self.COLORS["accent"])])

    def create_layout(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=self.COLORS["sidebar"], width=280)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_frame = tk.Frame(self.sidebar, bg=self.COLORS["sidebar"], pady=40)
        logo_frame.pack(fill="x")
        logo = tk.Label(logo_frame, text="GRAND HOTEL", font=("Segoe UI", 20, "bold"),
                        fg=self.COLORS["accent"], bg=self.COLORS["sidebar"])
        logo.pack()

        # Navigation Buttons
        self.create_sidebar_btn("Dashboard", "🏠", self.show_dashboard)
        self.create_sidebar_btn("Rooms", "🏢", self.show_rooms)
        self.create_sidebar_btn("Booking", "📅", self.show_reservation)
        self.create_sidebar_btn("Inventory", "🍱", self.show_inventory)
        self.create_sidebar_btn("History", "📜", self.show_history)
        self.create_sidebar_btn("Logout", "🚪", self.logout)

        # Content Area
        self.content_area = tk.Frame(self, bg=self.COLORS["bg"])
        self.content_area.pack(side="right", fill="both", expand=True)

        # Top Bar
        self.topbar = tk.Frame(self.content_area, bg=self.COLORS["card"], height=80)
        self.topbar.pack(side="top", fill="x")
        self.topbar.pack_propagate(False)

        self.page_title = tk.Label(self.topbar, text="Dashboard Overview", font=("Segoe UI", 18, "bold"),
                                  fg=self.COLORS["text_primary"], bg=self.COLORS["card"], padx=30)
        self.page_title.pack(side="left", pady=20)

        # Top Bar Search
        search_frame = tk.Frame(self.topbar, bg="#374151", padx=15, pady=8, highlightbackground=self.COLORS["border"], highlightthickness=1)
        search_frame.pack(side="right", padx=30, pady=18)
        tk.Label(search_frame, text="🔍", bg="#374151", fg=self.COLORS["text_secondary"]).pack(side="left")
        tk.Entry(search_frame, bg="#374151", fg="white", border=0, insertbackground="white", width=30, font=("Segoe UI", 10)).pack(side="left", padx=10)

        # Main Workspace
        self.main = tk.Frame(self.content_area, bg=self.COLORS["bg"])
        self.main.pack(fill="both", expand=True, padx=40, pady=(0, 40))

    def create_sidebar_btn(self, name, icon, command):
        btn_frame = tk.Frame(self.sidebar, bg=self.COLORS["sidebar"])
        btn_frame.pack(fill="x", pady=2)

        icon_label = tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 14),
                              fg=self.COLORS["text_secondary"], bg=self.COLORS["sidebar"])
        icon_label.pack(side="left", padx=(30, 10), pady=15)

        text_label = tk.Label(btn_frame, text=name, font=("Segoe UI", 12, "bold"),
                              fg=self.COLORS["text_secondary"], bg=self.COLORS["sidebar"],
                              anchor="w")
        text_label.pack(side="left", fill="x", expand=True)

        def on_click(event):
            command()
            self.set_active_nav(name)

        btn_frame.bind("<Button-1>", on_click)
        icon_label.bind("<Button-1>", on_click)
        text_label.bind("<Button-1>", on_click)
        
        btn_frame.bind("<Enter>", lambda e: self.on_nav_enter(name))
        btn_frame.bind("<Leave>", lambda e: self.on_nav_leave(name))

        self.sidebar_buttons[name] = {"frame": btn_frame, "icon": icon_label, "text": text_label}

    def on_nav_enter(self, name):
        if self.active_page != name:
            widgets = self.sidebar_buttons[name]
            widgets["frame"].config(bg="#374151")
            widgets["icon"].config(bg="#374151", fg="white")
            widgets["text"].config(bg="#374151", fg="white")

    def on_nav_leave(self, name):
        if self.active_page != name:
            widgets = self.sidebar_buttons[name]
            widgets["frame"].config(bg=self.COLORS["sidebar"])
            widgets["icon"].config(bg=self.COLORS["sidebar"], fg=self.COLORS["text_secondary"])
            widgets["text"].config(bg=self.COLORS["sidebar"], fg=self.COLORS["text_secondary"])

    def set_active_nav(self, nav_name):
        self.active_page = nav_name
        for name, widgets in self.sidebar_buttons.items():
            if name == nav_name:
                widgets["frame"].config(bg=self.COLORS["accent"])
                widgets["icon"].config(bg=self.COLORS["accent"], fg="white")
                widgets["text"].config(bg=self.COLORS["accent"], fg="white")
            else:
                widgets["frame"].config(bg=self.COLORS["sidebar"])
                widgets["icon"].config(bg=self.COLORS["sidebar"], fg=self.COLORS["text_secondary"])
                widgets["text"].config(bg=self.COLORS["sidebar"], fg=self.COLORS["text_secondary"])

    def clear_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_main()
        self.page_title.config(text="Dashboard Overview")
        self.set_active_nav("Dashboard")
        
        stats = database.get_dashboard_stats()
        
        # Stats Grid
        stats_frame = tk.Frame(self.main, bg=self.COLORS["bg"])
        stats_frame.pack(fill="x", pady=30)
        
        cards = [
            ("Total Bookings", stats["total_bookings"], self.COLORS["accent"]),
            ("Rooms Available", stats["rooms_available"], "#10B981"),
            ("Check-outs Today", stats["checkouts_today"], "#F59E0B"),
            ("Total Revenue", stats["total_revenue"], "#8B5CF6")
        ]
        
        for i, (title, val, color) in enumerate(cards):
            card = tk.Frame(stats_frame, bg=self.COLORS["card"], padx=25, pady=25, highlightbackground=self.COLORS["border"], highlightthickness=1)
            card.grid(row=0, column=i, padx=10, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)
            
            tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), fg=self.COLORS["text_secondary"], bg=self.COLORS["card"]).pack(anchor="w")
            tk.Label(card, text=val, font=("Segoe UI", 24, "bold"), fg=color, bg=self.COLORS["card"], pady=10).pack(anchor="w")

        # Recent Bookings Section
        tk.Label(self.main, text="Recent Bookings Status", font=("Segoe UI", 16, "bold"), 
                 fg=self.COLORS["text_primary"], bg=self.COLORS["bg"]).pack(anchor="w", pady=(20, 15))

        table_card = tk.Frame(self.main, bg=self.COLORS["card"], highlightbackground=self.COLORS["border"], highlightthickness=1)
        table_card.pack(fill="both", expand=True)

        table_header = tk.Frame(table_card, bg=self.COLORS["sidebar"], pady=15)
        table_header.pack(fill="x")
        cols = ["Guest Name", "Room", "Stay Period", "Total Cost", "Pay Status", "Status"]
        for i, col in enumerate(cols):
            lbl = tk.Label(table_header, text=col.upper(), font=("Segoe UI", 10, "bold"), fg=self.COLORS["accent"], bg=self.COLORS["sidebar"])
            lbl.grid(row=0, column=i, sticky="ew")
            table_header.grid_columnconfigure(i, weight=1)

        self.table_body = tk.Frame(table_card, bg=self.COLORS["card"])
        self.table_body.pack(fill="both", expand=True)
        self.update_table()

    def update_table(self):
        self.all_data = database.get_all_reservations()
        if not self.table_body: return
        for widget in self.table_body.winfo_children(): widget.destroy()

        # Display first 10
        for row_data in self.all_data[:10]:
            row = tk.Frame(self.table_body, bg=self.COLORS["card"], pady=12)
            row.pack(fill="x")
            tk.Frame(self.table_body, bg=self.COLORS["border"], height=1).pack(fill="x")

            for i, val in enumerate(row_data[:6]):
                row.grid_columnconfigure(i, weight=1)
                if i == 5: # Status
                    color = "#3B82F6" if val == "Confirmed" else ("#10B981" if val == "Checked-in" else "#F59E0B")
                    badge = tk.Frame(row, bg=color, padx=12, pady=4)
                    badge.grid(row=0, column=i)
                    tk.Label(badge, text=val.upper(), font=("Segoe UI", 9, "bold"), fg="white", bg=color).pack()
                else:
                    display_val = str(val).replace('$', 'GH₵ ').replace('GH₵ GH₵', 'GH₵')
                    tk.Label(row, text=display_val, font=("Segoe UI", 11), fg=self.COLORS["text_primary"], bg=self.COLORS["card"]).grid(row=0, column=i)

    def show_rooms(self):
        self.clear_main()
        self.page_title.config(text="Rooms Management")
        self.set_active_nav("Rooms")
        RoomsPage(self.main).pack(fill="both", expand=True)

    def show_reservation(self):
        self.clear_main()
        self.page_title.config(text="Reservation Management")
        self.set_active_nav("Booking")
        ReservationPage(self.main).pack(fill="both", expand=True)

    def show_inventory(self):
        self.clear_main()
        self.page_title.config(text="Inventory & POS")
        self.set_active_nav("Inventory")
        InventoryPage(self.main).pack(fill="both", expand=True)

    def show_history(self):
        self.clear_main()
        self.page_title.config(text="Booking History Archives")
        self.set_active_nav("History")
        HistoryPage(self.main).pack(fill="both", expand=True)

    def logout(self):
        if messagebox.askyesno("Logout", "Confirm Logout?"):
            self.master.destroy()
            import main as m
            m.main()
