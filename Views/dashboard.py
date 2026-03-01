# Redesigned Professional Dashboard
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

from Views.rooms import RoomsPage
from Views.reservation import ReservationPage
from Views.history import HistoryPage
from Views.inventory import InventoryPage 
from Views.menu_management import MenuManagementPage
from Views.history import HistoryPage
from Views.sales_history import SalesHistoryPage
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
        
        # Pagination
        self.current_page = 0
        self.rows_per_page = 10
        self.weights = [20, 10, 25, 15, 15, 15]
        self.cols = ["Guest Name", "Room", "Stay Period", "Total Cost", "Pay Status", "Status"]
        
        self.active_page = "Dashboard"
        self.sidebar_buttons = {} 
        self.sidebar = None
        self.content_area = None
        self.topbar = None
        self.page_title = None
        self.main = None
        self.header_frame = None
        self.pagination_frame = None

        self.setup_styles()
        self.create_layout()
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
        tk.Label(logo_frame, text="GRAND HOTEL", font=("Segoe UI", 20, "bold"),
                        fg=self.COLORS["accent"], bg=self.COLORS["sidebar"]).pack()

        # Navigation Buttons
        self.create_sidebar_btn("Dashboard", "🏠", self.show_dashboard)
        self.create_sidebar_btn("Rooms", "🏢", self.show_rooms)
        self.create_sidebar_btn("Booking", "📅", self.show_reservation)
        self.create_sidebar_btn("POS / Sales", "🛒", self.show_pos)
        self.create_sidebar_btn("Meal Menu", "🍱", self.show_menu)
        self.create_sidebar_btn("Sales History", "📈", self.show_sales_history)
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
        if self.page_title:
            self.page_title.pack(side="left", pady=20)

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
            w = self.sidebar_buttons[name]
            w["frame"].config(bg="#374151")
            w["icon"].config(bg="#374151", fg="white")
            w["text"].config(bg="#374151", fg="white")

    def on_nav_leave(self, name):
        if self.active_page != name:
            w = self.sidebar_buttons[name]
            w["frame"].config(bg=self.COLORS["sidebar"])
            w["icon"].config(bg=self.COLORS["sidebar"], fg=self.COLORS["text_secondary"])
            w["text"].config(bg=self.COLORS["sidebar"], fg=self.COLORS["text_secondary"])

    def set_active_nav(self, nav_name):
        self.active_page = nav_name
        for name, w in self.sidebar_buttons.items():
            if name == nav_name:
                w["frame"].config(bg=self.COLORS["accent"])
                w["icon"].config(bg=self.COLORS["accent"], fg="white")
                w["text"].config(bg=self.COLORS["accent"], fg="white")
            else:
                w["frame"].config(bg=self.COLORS["sidebar"])
                w["icon"].config(bg=self.COLORS["sidebar"], fg=self.COLORS["text_secondary"])
                w["text"].config(bg=self.COLORS["sidebar"], fg=self.COLORS["text_secondary"])

    def clear_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_main()
        self.page_title.config(text="Dashboard Overview")
        self.set_active_nav("Dashboard")
        
        stats = database.get_dashboard_stats()
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

        tk.Label(self.main, text="Recent Bookings Status", font=("Segoe UI", 16, "bold"), 
                 fg=self.COLORS["text_primary"], bg=self.COLORS["bg"]).pack(anchor="w", pady=(20, 15))

        table_card = tk.Frame(self.main, bg=self.COLORS["card"], highlightbackground=self.COLORS["border"], highlightthickness=1)
        table_card.pack(fill="both", expand=True)

        # Structural fix for exact column alignment: Header and Canvas share inner_container
        # Scrollbar is outside inner_container
        scrollbar = ttk.Scrollbar(table_card, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        inner_container = tk.Frame(table_card, bg=self.COLORS["card"])
        inner_container.pack(side="left", fill="both", expand=True)

        # Table Header (Inside inner_container)
        self.header_frame = tk.Frame(inner_container, bg=self.COLORS["sidebar"], pady=15, padx=20)
        self.header_frame.pack(fill="x")
        for i, col in enumerate(self.cols):
            tk.Label(self.header_frame, text=col.upper(), font=("Segoe UI", 10, "bold"), 
                     fg=self.COLORS["accent"], bg=self.COLORS["sidebar"]).grid(row=0, column=i, sticky="ew")
            self.header_frame.grid_columnconfigure(i, weight=self.weights[i])

        # Scrollable table container (Inside inner_container)
        canvas = tk.Canvas(inner_container, bg=self.COLORS["card"], highlightthickness=0, height=400)
        canvas.pack(fill="both", expand=True)
        
        self.table_body = tk.Frame(canvas, bg=self.COLORS["card"])
        self.canvas_window = canvas.create_window((0, 0), window=self.table_body, anchor="nw")
        
        def _on_canvas_configure(event):
            canvas.itemconfig(self.canvas_window, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)
        
        scrollbar.config(command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pagination Frame
        self.pagination_frame = tk.Frame(self.main, bg=self.COLORS["bg"], pady=10)
        self.pagination_frame.pack(fill="x")
        
        self.update_table()

    def update_table(self):
        if not self.table_body: return
        for widget in self.table_body.winfo_children(): widget.destroy()

        self.all_data = database.get_all_reservations()
        total_items = len(self.all_data)
        total_pages = max(1, (total_items + self.rows_per_page - 1) // self.rows_per_page)
        
        if self.current_page >= total_pages: self.current_page = total_pages - 1
        start = self.current_page * self.rows_per_page
        end = start + self.rows_per_page
        page_data = self.all_data[start:end]

        for row_data in page_data:
            row = tk.Frame(self.table_body, bg=self.COLORS["card"], pady=12, padx=20)
            row.pack(fill="x")
            
            for i in range(len(self.weights)):
                row.grid_columnconfigure(i, weight=self.weights[i])

            # Columns
            # 0: Name, 1: Room, 2: Stay Period, 3: Cost, 4: Pay Stat, 5: Status
            for i, val in enumerate(row_data[:6]):
                if i == 5: # Status Badge
                    color = "#3B82F6" if val == "Confirmed" else ("#10B981" if val == "Checked-in" else "#F59E0B")
                    badge_container = tk.Frame(row, bg=self.COLORS["card"])
                    badge_container.grid(row=0, column=i, sticky="ew")
                    badge = tk.Frame(badge_container, bg=color, padx=12, pady=4)
                    badge.pack()
                    tk.Label(badge, text=val.upper(), font=("Segoe UI", 9, "bold"), fg="white", bg=color).pack()
                else:
                    display_val = str(val).replace('$', 'GH₵ ').replace('GH₵ GH₵', 'GH₵')
                    tk.Label(row, text=display_val, font=("Segoe UI", 11), fg=self.COLORS["text_primary"], 
                             bg=self.COLORS["card"], anchor="w" if i != 1 else "center").grid(row=0, column=i, sticky="ew")
            
            tk.Frame(self.table_body, bg=self.COLORS["border"], height=1).pack(fill="x")

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
            self.update_table()

    def next_page(self):
        total_items = len(self.all_data)
        total_pages = (total_items + self.rows_per_page - 1) // self.rows_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_table()

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

    def show_pos(self):
        self.clear_main()
        self.page_title.config(text="Point of Sale (POS)")
        self.set_active_nav("POS / Sales")
        InventoryPage(self.main).pack(fill="both", expand=True)

    def show_menu(self):
        self.clear_main()
        self.page_title.config(text="Meal Menu Management")
        self.set_active_nav("Meal Menu")
        MenuManagementPage(self.main).pack(fill="both", expand=True)

    def show_sales_history(self):
        self.clear_main()
        self.page_title.config(text="Sales Performance History")
        self.set_active_nav("Sales History")
        SalesHistoryPage(self.main).pack(fill="both", expand=True)

    def show_history(self):
        self.clear_main()
        self.page_title.config(text="Booking History Archives")
        self.set_active_nav("History")
        HistoryPage(self.main).pack(fill="both", expand=True)

    def logout(self):
        if messagebox.askyesno("Logout", "Confirm Logout?"):
            self.master.destroy()
            # More robust way to restart the app correctly
            try:
                # Add root to sys.path to ensure main is found
                root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if root_path not in sys.path: sys.path.insert(0, root_path)
                import main as m
                # Refresh module if already imported
                import importlib
                importlib.reload(m)
                m.main()
            except Exception as e:
                print(f"Logout Error: {e}")
                os.execl(sys.executable, sys.executable, *sys.argv)
