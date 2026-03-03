# Redesigned Professional Dashboard
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime
from PIL import Image, ImageTk

from Views.rooms import RoomsPage
from Views.reservation import ReservationPage
from Views.history import HistoryPage
from Views.inventory import InventoryPage
from Views.menu_management import MenuManagementPage
from Views.sales_history import SalesHistoryPage
from Views.theme import COLORS, HOTEL_NAME, FONTS, LOGO_PNG, LOGO_ICO
import database

class DashboardWindow(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master.title(f"{HOTEL_NAME} – Management Dashboard")
        self.master.geometry("1400x900")
        self.pack(fill="both", expand=True)

        # Set window/taskbar icon
        try:
            self.master.iconbitmap(LOGO_ICO)
        except Exception:
            pass

        self._sidebar_logo_img = None  # prevent GC
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
        self.clock_label = None

        self.setup_styles()
        self.create_layout()
        self.show_dashboard()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=COLORS["card"], foreground="white",
                        fieldbackground=COLORS["card"], borderwidth=0)
        style.map("Treeview", background=[('selected', COLORS["accent"])])

    def create_layout(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=COLORS["sidebar"], width=280)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo area — image + text
        logo_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar"], pady=20)
        logo_frame.pack(fill="x")
        try:
            raw = Image.open(LOGO_PNG).convert("RGBA")
            raw = raw.resize((72, 72), Image.LANCZOS)
            self._sidebar_logo_img = ImageTk.PhotoImage(raw)
            tk.Label(logo_frame, image=self._sidebar_logo_img,
                     bg=COLORS["sidebar"]).pack(pady=(0, 6))
        except Exception:
            pass
        tk.Label(logo_frame, text=HOTEL_NAME, font=FONTS["logo"],
                 fg=COLORS["accent"], bg=COLORS["sidebar"]).pack()
        tk.Label(logo_frame, text="Management Suite", font=("Segoe UI", 10),
                 fg=COLORS["text_secondary"], bg=COLORS["sidebar"]).pack()

        # Divider
        tk.Frame(self.sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=20)

        # Navigation
        nav_items = [
            ("Dashboard",    "🏠", self.show_dashboard),
            ("Rooms",        "🏢", self.show_rooms),
            ("Booking",      "📅", self.show_reservation),
            ("POS / Sales",  "🛒", self.show_pos),
            ("Meal Menu",    "🍱", self.show_menu),
            ("Sales History","📈", self.show_sales_history),
            ("History",      "📜", self.show_history),
            ("Logout",       "🚪", self.logout),
        ]
        for name, icon, cmd in nav_items:
            self.create_sidebar_btn(name, icon, cmd)

        # Content Area
        self.content_area = tk.Frame(self, bg=COLORS["bg"])
        self.content_area.pack(side="right", fill="both", expand=True)

        # Top Bar
        self.topbar = tk.Frame(self.content_area, bg=COLORS["card"], height=70)
        self.topbar.pack(side="top", fill="x")
        self.topbar.pack_propagate(False)

        self.page_title = tk.Label(self.topbar, text="Dashboard Overview",
                                   font=FONTS["topbar"], fg=COLORS["text_primary"],
                                   bg=COLORS["card"], padx=30)
        self.page_title.pack(side="left", pady=15)

        # Live clock in top bar right
        self.clock_label = tk.Label(self.topbar, text="", font=("Segoe UI", 11),
                                    fg=COLORS["text_secondary"], bg=COLORS["card"], padx=20)
        self.clock_label.pack(side="right", pady=15)
        self._tick_clock()

        # Main Workspace
        self.main = tk.Frame(self.content_area, bg=COLORS["bg"])
        self.main.pack(fill="both", expand=True, padx=40, pady=(0, 40))

    def _tick_clock(self):
        """Update the clock label every second."""
        now = datetime.now().strftime("%a, %d %b %Y  •  %H:%M:%S")
        if self.clock_label:
            try:
                self.clock_label.config(text=now)
                self.clock_label.after(1000, self._tick_clock)
            except tk.TclError:
                pass  # widget was destroyed

    def create_sidebar_btn(self, name, icon, command):
        btn_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        btn_frame.pack(fill="x", pady=1)

        # Left accent bar (shown when active)
        accent_bar = tk.Frame(btn_frame, bg=COLORS["sidebar"], width=4)
        accent_bar.pack(side="left", fill="y")

        icon_label = tk.Label(btn_frame, text=icon, font=("Segoe UI Emoji", 14),
                               fg=COLORS["text_secondary"], bg=COLORS["sidebar"])
        icon_label.pack(side="left", padx=(20, 10), pady=14)

        text_label = tk.Label(btn_frame, text=name, font=("Segoe UI", 12, "bold"),
                              fg=COLORS["text_secondary"], bg=COLORS["sidebar"], anchor="w")
        text_label.pack(side="left", fill="x", expand=True)

        def on_click(event):
            command()
            self.set_active_nav(name)

        for w in (btn_frame, icon_label, text_label, accent_bar):
            w.bind("<Button-1>", on_click)
            w.bind("<Enter>", lambda e, n=name: self.on_nav_enter(n))
            w.bind("<Leave>", lambda e, n=name: self.on_nav_leave(n))

        self.sidebar_buttons[name] = {
            "frame": btn_frame, "icon": icon_label,
            "text": text_label, "bar": accent_bar
        }

    def on_nav_enter(self, name):
        if self.active_page != name:
            w = self.sidebar_buttons[name]
            w["frame"].config(bg="#374151")
            w["icon"].config(bg="#374151", fg="white")
            w["text"].config(bg="#374151", fg="white")
            w["bar"].config(bg="#374151")

    def on_nav_leave(self, name):
        if self.active_page != name:
            w = self.sidebar_buttons[name]
            w["frame"].config(bg=COLORS["sidebar"])
            w["icon"].config(bg=COLORS["sidebar"], fg=COLORS["text_secondary"])
            w["text"].config(bg=COLORS["sidebar"], fg=COLORS["text_secondary"])
            w["bar"].config(bg=COLORS["sidebar"])

    def set_active_nav(self, nav_name):
        self.active_page = nav_name
        for name, w in self.sidebar_buttons.items():
            if name == nav_name:
                w["frame"].config(bg=COLORS["accent"])
                w["icon"].config(bg=COLORS["accent"], fg="white")
                w["text"].config(bg=COLORS["accent"], fg="white")
                w["bar"].config(bg="#4338CA")  # deeper accent as left border
            else:
                w["frame"].config(bg=COLORS["sidebar"])
                w["icon"].config(bg=COLORS["sidebar"], fg=COLORS["text_secondary"])
                w["text"].config(bg=COLORS["sidebar"], fg=COLORS["text_secondary"])
                w["bar"].config(bg=COLORS["sidebar"])

    def clear_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_main()
        self.page_title.config(text="Dashboard Overview")
        self.set_active_nav("Dashboard")

        stats = database.get_dashboard_stats()
        stats_frame = tk.Frame(self.main, bg=COLORS["bg"])
        stats_frame.pack(fill="x", pady=30)

        cards = [
            ("📋 Total Bookings",   stats["total_bookings"],  COLORS["accent"]),
            ("🛏 Rooms Available",  stats["rooms_available"],  COLORS["success"]),
            ("🚪 Check-outs Today", stats["checkouts_today"],  COLORS["warning"]),
            ("💰 Total Revenue",    stats["total_revenue"],    "#8B5CF6"),
        ]

        for i, (title, val, color) in enumerate(cards):
            card = tk.Frame(stats_frame, bg=COLORS["card"], padx=25, pady=25,
                            highlightbackground=COLORS["border"], highlightthickness=1)
            card.grid(row=0, column=i, padx=10, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)
            tk.Label(card, text=title, font=("Segoe UI", 10, "bold"),
                     fg=COLORS["text_secondary"], bg=COLORS["card"]).pack(anchor="w")
            tk.Label(card, text=str(val), font=("Segoe UI", 26, "bold"),
                     fg=color, bg=COLORS["card"], pady=8).pack(anchor="w")
            # Thin color bar at bottom of card
            tk.Frame(card, bg=color, height=3).pack(fill="x", side="bottom")

        tk.Label(self.main, text="Recent Bookings Status", font=FONTS["heading"],
                 fg=COLORS["text_primary"], bg=COLORS["bg"]).pack(anchor="w", pady=(20, 12))

        table_card = tk.Frame(self.main, bg=COLORS["card"],
                              highlightbackground=COLORS["border"], highlightthickness=1)
        table_card.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_card, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        inner_container = tk.Frame(table_card, bg=COLORS["card"])
        inner_container.pack(side="left", fill="both", expand=True)

        self.header_frame = tk.Frame(inner_container, bg=COLORS["sidebar"], pady=14, padx=20)
        self.header_frame.pack(fill="x")
        # Anchors must match those used in data rows below
        col_anchors = ["w", "center", "center", "center", "center", "center"]
        for i, col in enumerate(self.cols):
            tk.Label(self.header_frame, text=col.upper(), font=FONTS["label"],
                     fg=COLORS["accent"], bg=COLORS["sidebar"],
                     anchor=col_anchors[i]).grid(row=0, column=i, sticky="ew")  # type: ignore[arg-type]
            self.header_frame.grid_columnconfigure(i, weight=self.weights[i], minsize=60)

        canvas = tk.Canvas(inner_container, bg=COLORS["card"], highlightthickness=0, height=380)
        canvas.pack(fill="both", expand=True)

        self.table_body = tk.Frame(canvas, bg=COLORS["card"])
        self.canvas_window = canvas.create_window((0, 0), window=self.table_body, anchor="nw")

        def _on_canvas_configure(event):
            canvas.itemconfig(self.canvas_window, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        scrollbar.config(command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        self.pagination_frame = tk.Frame(self.main, bg=COLORS["bg"], pady=10)
        self.pagination_frame.pack(fill="x")

        self.update_table()

    def update_table(self):
        if not self.table_body:
            return
        for widget in self.table_body.winfo_children():
            widget.destroy()

        self.all_data = database.get_all_reservations()
        total_items = len(self.all_data)
        total_pages = max(1, (total_items + self.rows_per_page - 1) // self.rows_per_page)

        if self.current_page >= total_pages:
            self.current_page = total_pages - 1
        start = self.current_page * self.rows_per_page
        page_data = self.all_data[start:start + self.rows_per_page]

        for idx, row_data in enumerate(page_data):
            row_bg = COLORS["card"] if idx % 2 == 0 else "#1a2332"
            row = tk.Frame(self.table_body, bg=row_bg, pady=11, padx=20)
            row.pack(fill="x")

            for i in range(len(self.weights)):
                row.grid_columnconfigure(i, weight=self.weights[i], minsize=60)

            for i, val in enumerate(row_data[:6]):
                if i == 5:  # Status badge — centered
                    color = (COLORS["info"]    if val == "Confirmed"  else
                             COLORS["success"] if val == "Checked-in" else
                             COLORS["warning"] if val == "Checked-out" else
                             COLORS["danger"])
                    bc = tk.Frame(row, bg=row_bg)
                    bc.grid(row=0, column=i, sticky="ew")
                    badge = tk.Frame(bc, bg=color, padx=12, pady=3)
                    badge.pack(anchor="center")
                    tk.Label(badge, text=val.upper(), font=FONTS["badge"], fg="white", bg=color).pack()
                else:
                    txt = str(val).replace('$', 'GH\u20b5 ').replace('GH\u20b5  GH\u20b5', 'GH\u20b5')
                    # Col 0 = Guest Name: left-aligned; all others: center
                    anc = "w" if i == 0 else "center"
                    tk.Label(row, text=txt, font=("Segoe UI", 11),
                             fg=COLORS["text_primary"],
                             bg=row_bg, anchor=anc).grid(row=0, column=i, sticky="ew")

            tk.Frame(self.table_body, bg=COLORS["border"], height=1).pack(fill="x")

        self.update_table_scroll()
        self.update_pagination_controls(total_pages)

    def update_table_scroll(self):
        try:
            self.table_body.update_idletasks()
            canvas = self.table_body.master
            canvas.config(scrollregion=canvas.bbox("all"))
        except Exception:
            pass

    def update_pagination_controls(self, total_pages):
        for widget in self.pagination_frame.winfo_children():
            widget.destroy()

        inner_p = tk.Frame(self.pagination_frame, bg=COLORS["bg"])
        inner_p.pack()

        def make_btn(text, cmd, active):
            return tk.Button(inner_p, text=text, font=("Segoe UI", 10, "bold"),
                             fg="white" if active else COLORS["text_secondary"],
                             bg=COLORS["sidebar"] if active else COLORS["bg"],
                             bd=0, padx=15, pady=8,
                             cursor="hand2" if active else "arrow",
                             command=cmd)

        make_btn("← Prev", self.prev_page, self.current_page > 0).pack(side="left", padx=5)
        tk.Label(inner_p, text=f"Page {self.current_page + 1} of {total_pages}",
                 font=("Segoe UI", 11), fg=COLORS["text_primary"], bg=COLORS["bg"]).pack(side="left", padx=20)
        make_btn("Next →", self.next_page, self.current_page < total_pages - 1).pack(side="left", padx=5)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_table()

    def next_page(self):
        total_pages = max(1, (len(self.all_data) + self.rows_per_page - 1) // self.rows_per_page)
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
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            try:
                self.master.destroy()
            except Exception:
                pass
            # Restart cleanly without importlib hacks
            python = sys.executable
            os.execl(python, python, *sys.argv)
