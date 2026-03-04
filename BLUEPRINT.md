# 🏨 Nona Lodge — Hotel Management System
## Agent Build Blueprint · Upgrade Edition

> **READ THIS FIRST (Agent Instructions):**
> This document is the complete specification for building an upgraded version of the **Nona Lodge Hotel Management System**. You are to use this as your single source of truth. Do **not** replicate bugs or legacy patterns from the original — use modern equivalents throughout. Every section marked `[AGENT DIRECTIVE]` is a direct instruction to you.

---

## 1. Project Purpose

**Nona Lodge Hotel Management System** is a full-featured, single-operator desktop application for managing a small-to-medium hotel. It replaces paper-based workflows with a digital front desk that handles:

- Guest check-in / check-out lifecycle
- Room inventory and availability tracking
- Restaurant and room-service Point of Sale (POS)
- Booking history and revenue reporting
- Meal/menu item management
- Staff authentication (login / signup)

The application is used **on-premises** by a single logged-in staff member at a time. Internet connectivity is **not required** at runtime. All data is stored in a local SQLite database.

---

## 2. Current Stack (Reference — Do Not Copy Blindly)

| Layer | Current |
|---|---|
| Language | Python 3.x with `tkinter` |
| UI toolkit | `tkinter` + `ttk` (stdlib) |
| Styling | Manual hex-color dark theme via `Views/theme.py` |
| Database | SQLite3 via stdlib `sqlite3` |
| Date picker | `tkcalendar` |
| Image handling | `Pillow` (`PIL`) |
| Packaging | PyInstaller (single-file exe) |
| Auth | SHA-256 hashed passwords (stdlib `hashlib`) |

---

## 3. [AGENT DIRECTIVE] — Upgraded Target Stack

> Use **every item below** at its latest stable release at time of build. Pin exact versions in `requirements.txt` after resolving.

### 3.1 Runtime
- **Python 3.13+** — use features: `match/case`, `tomllib`, `f-string` improvements, `pathlib` everywhere. No `os.path`.
- **Virtual environment** — always create and activate a `venv` before installing anything.

### 3.2 UI Framework — CustomTkinter
Replace raw `tkinter` with **`customtkinter>=5.2`**. This provides:
- Native-looking dark/light mode widgets
- Rounded corners, smooth gradients, modern typography out of the box
- Drop-in `CTk*` widget replacements (`CTkFrame`, `CTkButton`, `CTkEntry`, `CTkLabel`, etc.)
- Built-in `set_appearance_mode("dark")` and `set_default_color_theme("blue")`

**Do not use** raw `tk.Button`, `tk.Label`, etc. Use `ctk.CTk*` equivalents everywhere.

### 3.3 Supporting UI Libraries
| Package | Purpose |
|---|---|
| `customtkinter>=5.2` | Primary UI framework |
| `Pillow>=11.0` | Image loading / logo display |
| `tkcalendar>=1.6` | Date picker in booking form |
| `sv-ttk>=2.6` OR use CTk natively | Theme fallback if needed |
| `CTkTable>=0.9` | Clean tabular data display (replaces manual grid rows) |
| `CTkMessagebox>=2.5` | Modern styled dialogs (replaces `messagebox`) |

### 3.4 Database
- Keep **SQLite3** (stdlib) — no ORM needed at this scale
- Add **`schema_version` table** for schema migration management
- Use **`contextlib.closing`** for all connections (no manual `conn.close()`)
- Use **parameterized queries exclusively** — no string formatting in SQL

### 3.5 Utilities
| Package | Purpose |
|---|---|
| `python-dotenv>=1.0` | For any future env config |
| `bcrypt>=4.1` | Replace SHA-256 with proper password hashing |
| `babel>=2.14` | Currency formatting (GH₵) |
| `pyinstaller>=6.0` | Packaging (single-file exe) |

### 3.6 `requirements.txt` Template
```
customtkinter>=5.2.2
Pillow>=11.0.0
tkcalendar>=1.6.1
CTkTable>=0.9
CTkMessagebox>=2.5
bcrypt>=4.1.3
babel>=2.14.0
python-dotenv>=1.0.1
pyinstaller>=6.19.0
```

---

## 4. Database Schema (Preserve + Extend)

### 4.1 Existing Tables — Keep All

```sql
-- Users: authentication
CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email    TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL  -- bcrypt hash
);

-- Rooms: hotel inventory
CREATE TABLE IF NOT EXISTS rooms (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number TEXT UNIQUE NOT NULL,
    type        TEXT NOT NULL,       -- 'Single', 'Double', 'Suite', etc.
    status      TEXT NOT NULL,       -- 'Available', 'Occupied', 'Maintenance'
    price       REAL NOT NULL
);

-- Reservations: guest bookings
CREATE TABLE IF NOT EXISTS reservations (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_name   TEXT NOT NULL,
    phone        TEXT NOT NULL,
    id_number    TEXT,
    room_id      INTEGER REFERENCES rooms(id),
    check_in     DATE NOT NULL,
    check_out    DATE NOT NULL,
    days         INTEGER NOT NULL,
    cost         REAL NOT NULL,
    pay_status   TEXT NOT NULL,      -- 'Paid', 'Unpaid'
    status       TEXT DEFAULT 'Confirmed'  -- 'Confirmed', 'Checked-in', 'Checked-out'
);

-- Inventory Items: restaurant/room-service items
CREATE TABLE IF NOT EXISTS inventory_items (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT NOT NULL,
    type  TEXT NOT NULL,    -- 'Restaurant' or 'Room Service'
    price REAL NOT NULL
);

-- Sales: POS transactions
CREATE TABLE IF NOT EXISTS sales (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id         INTEGER REFERENCES inventory_items(id),
    reservation_id  INTEGER REFERENCES reservations(id),  -- NULL = Instant Pay
    quantity        INTEGER NOT NULL,
    total_cost      REAL NOT NULL,
    payment_method  TEXT NOT NULL,  -- 'Instant' or 'Room Charge'
    sale_date       DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 New Tables to Add

```sql
-- Schema versioning for future migrations
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Audit log: track key actions
CREATE TABLE IF NOT EXISTS audit_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    action     TEXT NOT NULL,      -- 'CHECK_IN', 'CHECK_OUT', 'SALE', etc.
    entity     TEXT NOT NULL,      -- 'reservation', 'room', 'sale'
    entity_id  INTEGER,
    details    TEXT,               -- JSON string of changed fields
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4.3 Database Module Pattern
```python
# database.py — use context managers throughout
from contextlib import closing
import sqlite3, bcrypt

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect("nona_lodge.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def verify_user(username: str, password: str) -> bool:
    with closing(get_connection()) as conn:
        row = conn.execute(
            "SELECT password FROM users WHERE username = ?", (username,)
        ).fetchone()
    return row is not None and bcrypt.checkpw(password.encode(), row["password"])
```

---

## 5. Application Architecture

### 5.1 Directory Structure
```
nona_lodge/
├── main.py                  # Entry point
├── database.py              # All DB access functions
├── config.py                # App-wide constants (name, paths, colours)
├── requirements.txt
├── assets/
│   ├── logo.png             # 1024x1024 Nona Lodge logo
│   └── logo.ico             # Multi-res ICO for window icon
├── views/
│   ├── __init__.py
│   ├── login.py             # LoginWindow
│   ├── signup.py            # SignupWindow
│   ├── dashboard.py         # DashboardWindow (shell + nav)
│   ├── rooms.py             # RoomsPage
│   ├── reservation.py       # ReservationPage
│   ├── pos.py               # POSPage (was inventory.py)
│   ├── meal_menu.py         # MealMenuPage
│   ├── history.py           # BookingHistoryPage
│   └── sales_history.py     # SalesHistoryPage
└── nona_lodge.spec          # PyInstaller spec
```

### 5.2 Entry Point Pattern
```python
# main.py
import customtkinter as ctk
from views.login import LoginWindow
import database

def main():
    database.init_db()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = ctk.CTk()
    app.withdraw()
    LoginWindow(master=app)
    app.mainloop()

if __name__ == "__main__":
    main()
```

---

## 6. Feature Specification — All Modules

### 6.1 Login Page
**Layout:** Split-panel (left: branding, right: form)

- Left panel: Nona Lodge logo (180px), hotel name, tagline
- Right panel: Card with username + password fields, Login button, link to signup
- **Features:**
  - Password visibility toggle (eye icon button)
  - `<Return>` key submits form
  - Inline validation error labels (red, below each field)
  - Hover effect on login button (`accent_hover` color)
  - Window icon set from `assets/logo.ico`
  - `bcrypt` password verification

### 6.2 Signup Page
**Layout:** Centered card

- Fields: Username, Email, Password, Confirm Password
- **Features:**
  - Real-time password strength meter (Weak / Medium / Strong / Very Strong)
  - Password visibility toggles on both password fields
  - Inline validation: empty fields, email format, password match
  - `bcrypt` password hashing on save

### 6.3 Dashboard (Shell)
**Layout:** Fixed sidebar (280px) + scrollable main content area

**Sidebar contains:**
- Logo image (72px) + "Nona Lodge" + "Management Suite" subtitle
- Nav buttons: Dashboard, Rooms, Booking, POS / Sales, Meal Menu, Sales History, History, Logout
- Active state: accent background, bold text
- Hover state: subtle highlight

**Top bar contains:**
- Page title (dynamic)
- Live clock (updates every second, format: `Tue, 03 Mar 2026  •  13:04:23`)

**Dashboard home page contains:**
- **4 stat cards:** Total Bookings, Rooms Available, Check-outs Today, Total Revenue (GH₵)
  - Each card: icon, value in accent color, thin colored bar at bottom
- **Recent Bookings Status table:** scrollable, paginated (10/page)
  - Columns: Guest Name | Room | Stay Period | Total Cost | Pay Status | Status
  - Status badges: Confirmed (blue), Checked-in (green), Checked-out (orange), with color-coded backgrounds
  - Header anchors must match data row anchors exactly to avoid misalignment

### 6.4 Rooms Page
**Layout:** Scrollable card list

**Header:** Title + status filter buttons (All / Available / Occupied / Maintenance) + "Add Room" button

**Room cards (each row):** Room Number | Type | Status badge | Price | Edit (✏) | Delete buttons

**Add/Edit Room dialog:** Modal with fields: Room Number, Type (dropdown), Status (dropdown), Price

**Features:**
- Filter buttons update the visible list in real-time
- Price stored and displayed as `REAL` (no currency prefix stored)
- Status badge colors: Available=green, Occupied=red, Maintenance=orange
- Scrolling via mousewheel; `scrollregion` updated after each render

### 6.5 Booking / Reservation Page
**Layout:** Top form + bottom data table (both scrollable as one page)

**Booking Form fields:**
| Field | Widget |
|---|---|
| Guest Name | Text entry |
| Phone | Text entry |
| ID Number | Text entry |
| Room | Dropdown (available rooms only) |
| Check-in | DateEntry (tkcalendar) |
| Check-out | DateEntry (tkcalendar) |
| Days | Auto-calculated on date change |
| Total Cost | Auto-calculated: days × room_price |
| Pay Status | Dropdown: Paid / Unpaid |

**Form buttons:** Book Room, Update Booking, Clear Form, Check Out, Extend Stay

**Features:**
- Selecting a room auto-fills its current price
- Changing dates auto-recalculates days and cost
- "Extend Stay" opens modal asking for extra days; recalculates cost + checkout date
- "Check Out" sets reservation status = 'Checked-out', room status = 'Available'
- Editing: clicking a table row populates the form
- Validation: no empty fields, check-in must be before check-out, cost must be numeric

**Table below form:** Same columns as dashboard Recent Bookings table

### 6.6 POS / Sales Page (was InventoryPage)
**Layout:** Full-width POS card + transaction log table below

**POS Card:**
- Sale method radio: **Restaurant (Instant Pay)** | **Room Charge (Bill to Guest)**
- Item selector dropdown (populated from `inventory_items`)
- Auto-fills unit price when item selected
- Quantity spinner (1–100)
- Unit price editable entry
- Room selector dropdown (shown only for Room Charge; lists active reservations)
- Room balance display: "Guest: [name] | Room Balance: GH₵ X"
- "Confirm Transaction" button

**Transaction Log table:**
- Columns: ID | Item | Qty | Total | Method | Date | Guest | Room
- Paginated (10/page), searchable
- Method badge: Instant=green, Room Charge=blue

### 6.7 Meal Menu Page
**Layout:** Header (title + search + create button) + scrollable table

**Header:**
- "🍱 Meal Menu Management" title (left)
- Search bar (right, before button)
- "+ Create New Meal" button (rightmost, accent color) — **must be packed before search bar**

**Table columns:** Meal Name | Price (GH₵) | Actions
- Column weights: `[3, 2, 1]` with `minsize=80`
- Header anchors: `["w", "center", "center"]`
- Data anchors: `["w", "center", "center"]` — **header and data must match exactly**
- Delete button centered under "ACTIONS" column

**Add Meal dialog:** Modal with Name field + Price field + Save button

### 6.8 Booking History Page
**Layout:** Header (title + Export CSV button) + scrollable table

**Columns:** Guest | Room | Check-in | Check-out | Days | Cost | Pay Status | Booking Status

**Features:**
- Paginated (10/page)
- "⬇ Export CSV" button writes current view to a user-selected CSV file

### 6.9 Sales History Page
**Layout:** Header (title + Export CSV) + table

**Columns:** ID | Item | Qty | Total Cost | Method | Sale Date | Guest | Room

**Features:**
- Paginated
- "⬇ Export CSV" identical pattern to Booking History

---

## 7. Design System

### 7.1 Color Palette
```python
COLORS = {
    "bg":             "#111827",   # Page background (darkest)
    "sidebar":        "#1F2937",   # Sidebar + card backgrounds
    "card":           "#1F2937",   # Content cards
    "accent":         "#6366F1",   # Primary action color (indigo)
    "accent_hover":   "#4F46E5",   # Button hover state
    "text_primary":   "#F9FAFB",   # Main text
    "text_secondary": "#9CA3AF",   # Labels, subtitles
    "border":         "#374151",   # Card borders, dividers
    "success":        "#10B981",   # Available, paid, confirmed
    "danger":         "#EF4444",   # Delete, occupied, error
    "warning":        "#F59E0B",   # Maintenance, pending, checked-out
    "info":           "#3B82F6",   # Info badge, confirmed status
}
```

### 7.2 Typography
```python
FONTS = {
    "logo":    ("Segoe UI", 20, "bold"),
    "title":   ("Segoe UI", 24, "bold"),
    "heading": ("Segoe UI", 18, "bold"),
    "label":   ("Segoe UI", 10, "bold"),
    "body":    ("Segoe UI", 11),
    "small":   ("Segoe UI", 9, "bold"),
    "badge":   ("Segoe UI", 8, "bold"),
    "btn":     ("Segoe UI", 12, "bold"),
    "topbar":  ("Segoe UI", 18, "bold"),
}
```

### 7.3 Key Layout Rules

> These rules exist because the original had repeated alignment bugs. **Do not violate them.**

1. **Table header/data alignment:** Every column's `anchor` in the header label must exactly match the `anchor` in the data row label. Use explicit tuple lists per column, never index from `list[str]`.
2. **`side="right"` pack order:** Right-packed widgets must be `.pack()`d **before** left-packed widgets in the same frame. Otherwise tkinter crowds them out.
3. **Scrollable content:** Always:
   - Create canvas → place scrollable frame inside via `create_window`
   - Bind `<Configure>` on canvas to update `scrollregion`
   - Call `update_idletasks()` + `config(scrollregion=bbox("all"))` after adding rows
   - Bind `<MouseWheel>` with `bind_all` and unbind on `<Destroy>` to avoid `TclError`
4. **`minsize` on grid columns:** Always set `minsize=60` (or appropriate value) on all `grid_columnconfigure` calls to prevent collapse on narrow windows.
5. **`trace_add` signature:** The callback must accept **3 arguments**: `(name, index, op)`.
6. **Price storage:** Store prices as `REAL` in DB. Strip all currency prefixes/commas before `float()` conversion. Use `try/except` with meaningful fallback.
7. **`command=` must be callable:** Never pass `None` or a `BoundMethod | None` union as `command`. Use `lambda: None` as no-op for inactive buttons.

---

## 8. Feature Upgrades (New in This Build)

> These are net-new features the original did not have. Implement all of them.

### 8.1 Dashboard Enhancements
- [ ] **Revenue chart:** Embed a simple bar chart (use `matplotlib` with `FigureCanvasTkAgg`) showing daily revenue for the past 7 days
- [ ] **Occupancy rate card:** `Occupied / Total Rooms × 100%` with a circular progress indicator
- [ ] **Quick Actions:** "New Booking", "Check-in Guest", "Process Sale" shortcut buttons

### 8.2 Rooms Page
- [ ] **Room thumbnail/type icon** per room type (Single/Double/Suite)
- [ ] **Bulk status update:** Select multiple rooms and change status at once

### 8.3 Booking Page
- [ ] **Guest search / autocomplete:** As the user types a guest name in the form, suggest matching past guests from DB
- [ ] **Invoice generation:** "Print Invoice" button generates a formatted PDF using `fpdf2`
- [ ] **Email confirmation stub:** Show a "Send Confirmation" button (placeholder for SMTP integration)

### 8.4 POS Page
- [ ] **Receipt popup:** After confirming a transaction, show a styled receipt panel with item, qty, total, method, timestamp

### 8.5 Reports Page (New)
- [ ] New nav item: **"Reports"**
- [ ] Date-range revenue report (filter by check-in date range)
- [ ] Top 5 best-selling menu items
- [ ] Room occupancy timeline (which rooms were occupied on which dates)

### 8.6 Settings Page (New)
- [ ] New nav item: **"Settings"**
- [ ] Change hotel name (writes to a `config.toml`)
- [ ] Change logo (opens file picker, copies to assets folder)
- [ ] Change accent color (color picker)
- [ ] Export full database backup (copies `.db` file to user-chosen location)

### 8.7 Global UX
- [ ] **Notification toasts:** Non-blocking success/error toasts (bottom-right, auto-dismiss after 3s)
- [ ] **Keyboard shortcuts:** `Ctrl+N` = New Booking, `Ctrl+S` = Quick Sale, `Escape` = Close dialog
- [ ] **Confirmation dialogs:** Use `CTkMessagebox` everywhere instead of `tk.messagebox`
- [ ] **Loading spinners:** Show a spinner during any DB operation > 100ms

---

## 9. Packaging Spec

### 9.1 PyInstaller Spec
```python
# nona_lodge.spec — single-file build
a = Analysis(
    ['main.py'],
    datas=[
        ('nona_lodge.db', '.'),
        ('assets',        'assets'),
        ('views',         'views'),
    ],
    hiddenimports=[
        'customtkinter', 'PIL', 'PIL.Image', 'PIL.ImageTk',
        'tkcalendar', 'babel.numbers', 'bcrypt', 'fpdf2',
        'matplotlib', 'matplotlib.backends.backend_tkagg',
    ],
)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas,
    name='NonaLodge', console=False, icon='assets/logo.ico')
```

### 9.2 Build Command
```bash
pyinstaller nona_lodge.spec --clean --noconfirm
```

Output: `dist/NonaLodge.exe` — single distributable file, no dependencies needed on target machine.

---

## 10. Additional Packages for New Features

```
# Add to requirements.txt for upgraded build
matplotlib>=3.9.0     # Revenue charts
fpdf2>=2.8.0          # Invoice/PDF generation
CTkTable>=0.9         # Table widget
CTkMessagebox>=2.5    # Styled dialogs
```

---

## 11. Known Issues in Original — Do Not Repeat

| Bug | Root Cause | Fix |
|---|---|---|
| Rooms tab blank on startup | `float("GH₵ 150.00")` raises `ValueError` | Strip currency prefix before parsing |
| Create New Meal button clipped | Button packed after search bar (no space left) | Always pack `side="right"` widgets first |
| Header/data alignment in all tables | Header labels had no `anchor`, data used `"w"` | Add explicit anchor matching data per column |
| `trace_add` lambda errors | `lambda *args` doesn't match required `(name, index, op)` signature | Use `lambda name, index, op: ...` |
| Mouse scroll `TclError` on page switch | `bind_all` persists after widget destruction | Unbind in `<Destroy>` event handler |
| `command=None` on inactive buttons | Pyre2 strict mode + runtime issues | Use `lambda: None` for no-ops |
| SHA-256 password hashing | Not salted, vulnerable to rainbow tables | Replace with `bcrypt` |

---

## 12. Agent Checklist

When building this project, complete items in this order:

- [ ] Set up Python 3.13+ venv, install all packages from `requirements.txt`
- [ ] Create `config.py` with `HOTEL_NAME`, `COLORS`, `FONTS`, logo paths using `pathlib`
- [ ] Build `database.py` with all 7 tables, `bcrypt` auth, context-manager pattern
- [ ] Build `main.py` entry point (CTk init, dark mode, login window)
- [ ] Build `views/login.py` — split panel, logo, validation, bcrypt verify
- [ ] Build `views/signup.py` — password strength meter, bcrypt hash
- [ ] Build `views/dashboard.py` — sidebar nav, top bar clock, stat cards, recent bookings table
- [ ] Build `views/rooms.py` — filter buttons, room cards, CRUD dialog
- [ ] Build `views/reservation.py` — booking form + table, extend stay, checkout
- [ ] Build `views/pos.py` — POS card, transaction log, receipt popup
- [ ] Build `views/meal_menu.py` — header/table/dialog, correct column alignment
- [ ] Build `views/history.py` — table + CSV export
- [ ] Build `views/sales_history.py` — table + CSV export
- [ ] Build `views/reports.py` — revenue chart, top items, occupancy
- [ ] Build `views/settings.py` — hotel name, logo, accent color, DB backup
- [ ] Implement notification toast system
- [ ] Implement keyboard shortcuts
- [ ] Implement PDF invoice generation with `fpdf2`
- [ ] Write `nona_lodge.spec` and verify `pyinstaller` single-file build
- [ ] Test all pages: data loads, CRUD works, scrolling works, no `TclError` on page switch
- [ ] Verify exe runs on a clean machine (no Python installed)


