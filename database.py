import sqlite3
import hashlib
from datetime import datetime, timedelta

DB_NAME = "hotel_management.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Create Rooms table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL,
        status TEXT NOT NULL,
        price REAL NOT NULL
    )
    ''')
    
    # Create Reservations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        id_number TEXT,
        room_id INTEGER,
        check_in DATE NOT NULL,
        check_out DATE NOT NULL,
        days INTEGER NOT NULL,
        cost REAL NOT NULL,
        pay_status TEXT NOT NULL,
        status TEXT DEFAULT 'Confirmed',
        FOREIGN KEY (room_id) REFERENCES rooms (id)
    )
    ''')
    
    # Create Inventory Items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL, -- 'Restaurant' or 'Room Service'
        price REAL NOT NULL
    )
    ''')
    
    # Create Sales table (POS)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        reservation_id INTEGER, -- NULL for 'Instant Pay'
        quantity INTEGER NOT NULL,
        total_cost REAL NOT NULL,
        payment_method TEXT NOT NULL, -- 'Instant' or 'Room Charge'
        sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES inventory_items (id),
        FOREIGN KEY (reservation_id) REFERENCES reservations (id)
    )
    ''')
    
    # Migration: Add status column if it doesn't exist (Reservations)
    try:
        cursor.execute("ALTER TABLE reservations ADD COLUMN status TEXT DEFAULT 'Confirmed'")
    except sqlite3.OperationalError:
        pass 
        
    conn.commit()
    conn.close()

# --- User Helpers ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, email, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        hashed = hash_password(password)
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                       (username, email, hashed))
        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Username or Email already exists."
    except Exception as e:
        return False, str(e)

def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# --- Room Helpers ---
def add_room(room_number, r_type, status, price):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO rooms (room_number, type, status, price) VALUES (?, ?, ?, ?)",
                       (room_number, r_type, status, price))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_rooms():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_number, type, status, price FROM rooms")
    rooms = cursor.fetchall()
    conn.close()
    return rooms

def update_room(room_number, r_type, status, price, old_number=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        target = old_number if old_number else room_number
        cursor.execute('''
            UPDATE rooms 
            SET room_number = ?, type = ?, status = ?, price = ?
            WHERE room_number = ?
        ''', (room_number, r_type, status, price, target))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def delete_room(room_number):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rooms WHERE room_number = ?", (room_number,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

# --- Reservation Helpers ---
def add_reservation(guest_name, phone, id_number, room_number, check_in, check_out, days, cost, pay_status, res_id=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM rooms WHERE room_number = ?", (room_number,))
        room = cursor.fetchone()
        room_id = room[0] if room else None
        
        if res_id:
            cursor.execute('''
                UPDATE reservations 
                SET guest_name=?, phone=?, id_number=?, room_id=?, check_in=?, check_out=?, days=?, cost=?, pay_status=?
                WHERE id=?
            ''', (guest_name, phone, id_number, room_id, check_in, check_out, days, cost, pay_status, res_id))
        else:
            cursor.execute('''
                INSERT INTO reservations (guest_name, phone, id_number, room_id, check_in, check_out, days, cost, pay_status, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed')
            ''', (guest_name, phone, id_number, room_id, check_in, check_out, days, cost, pay_status))
            cursor.execute("UPDATE rooms SET status = 'Occupied' WHERE id = ?", (room_id,))
        
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_all_reservations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.guest_name, rm.room_number, r.check_in || ' - ' || r.check_out as dates, 
               r.cost, r.pay_status, r.status, r.id, r.phone, r.id_number, r.check_in, r.check_out, r.days
        FROM reservations r
        LEFT JOIN rooms rm ON r.room_id = rm.id
        ORDER BY r.id DESC
    ''')
    res = cursor.fetchall()
    conn.close()
    return res

def update_payment_status(res_id, status):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE reservations SET pay_status = ? WHERE id = ?", (status, res_id))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_reservation_by_id(res_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, rm.price as room_rate, rm.room_number
        FROM reservations r
        JOIN rooms rm ON r.room_id = rm.id
        WHERE r.id = ?
    ''', (res_id,))
    res = cursor.fetchone()
    conn.close()
    return res

def get_active_reservations():
    # Helper for Inventory "Room Charge" dropdown
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.id, r.guest_name, rm.room_number
        FROM reservations r
        JOIN rooms rm ON r.room_id = rm.id
        WHERE r.status != 'Checked-out'
    ''')
    res = cursor.fetchall()
    conn.close()
    return res

def extend_reservation_stay(res_id, extra_days):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get current reservation and room price
        cursor.execute('''
            SELECT r.days, r.cost, r.check_out, rm.price
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.id
            WHERE r.id = ?
        ''', (res_id,))
        data = cursor.fetchone()
        if not data: return False
        
        curr_days, curr_cost, curr_checkout, room_price = data
        new_days = curr_days + extra_days
        new_cost = curr_cost + (extra_days * room_price)
        
        # Calculate new checkout date
        checkout_dt = datetime.strptime(curr_checkout, "%Y-%m-%d")
        new_checkout = (checkout_dt + timedelta(days=extra_days)).strftime("%Y-%m-%d")
        
        cursor.execute('''
            UPDATE reservations 
            SET days = ?, cost = ?, check_out = ?
            WHERE id = ?
        ''', (new_days, new_cost, new_checkout, res_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error extending stay: {e}")
        return False

def checkout_reservation(res_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT room_id FROM reservations WHERE id = ?", (res_id,))
        res_data = cursor.fetchone()
        if not res_data: return False
        room_id = res_data[0]
        
        cursor.execute("UPDATE reservations SET status = 'Checked-out' WHERE id = ?", (res_id,))
        cursor.execute("UPDATE rooms SET status = 'Available' WHERE id = ?", (room_id,))
        
        conn.commit()
        conn.close()
        return True
    except:
        return False

# --- Inventory & Sales Helpers ---
def add_inventory_item(name, i_type, price):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventory_items (name, type, price) VALUES (?, ?, ?)",
                       (name, i_type, price))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_inventory_items():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, type, price FROM inventory_items")
    items = cursor.fetchall()
    conn.close()
    return items

def delete_inventory_item(item_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory_items WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def record_sale(item_id, quantity, payment_method, reservation_id=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get item price
        cursor.execute("SELECT price FROM inventory_items WHERE id = ?", (item_id,))
        price = cursor.fetchone()[0]
        total_cost = price * quantity
        
        # Record sale
        cursor.execute('''
            INSERT INTO sales (item_id, reservation_id, quantity, total_cost, payment_method)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_id, reservation_id, quantity, total_cost, payment_method))
        
        # If 'Room Charge', increase the reservation total cost
        if payment_method == 'Room Charge' and reservation_id:
            cursor.execute("UPDATE reservations SET cost = cost + ? WHERE id = ?", (total_cost, reservation_id))
            
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error recording sale: {e}")
        return False

def record_sale_manual(item_id, quantity, payment_method, manual_price, reservation_id=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        total_cost = manual_price * quantity
        
        cursor.execute('''
            INSERT INTO sales (item_id, reservation_id, quantity, total_cost, payment_method)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_id, reservation_id, quantity, total_cost, payment_method))
        
        if payment_method == 'Room Charge' and reservation_id:
            cursor.execute("UPDATE reservations SET cost = cost + ? WHERE id = ?", (total_cost, reservation_id))
            
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error recording sale: {e}")
        return False

def get_reservation_balance(res_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT cost FROM reservations WHERE id = ?", (res_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0
    except:
        return 0

def get_sales_report():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.id, i.name, s.quantity, s.total_cost, s.payment_method, s.sale_date, r.guest_name, rm.room_number
        FROM sales s
        JOIN inventory_items i ON s.item_id = i.id
        LEFT JOIN reservations r ON s.reservation_id = r.id
        LEFT JOIN rooms rm ON r.room_id = rm.id
        ORDER BY s.sale_date DESC
    ''')
    res = cursor.fetchall()
    conn.close()
    return res

def get_daily_sales_stats():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Sales today
    cursor.execute("SELECT COUNT(*), SUM(total_cost) FROM sales WHERE DATE(sale_date) = DATE('now')")
    stats = cursor.fetchone()
    daily_count = stats[0] or 0
    daily_revenue = stats[1] or 0
    
    # Total revenue from all time (Sales)
    cursor.execute("SELECT SUM(total_cost) FROM sales")
    total_sales_revenue = cursor.fetchone()[0] or 0
    
    conn.close()
    return {
        "daily_count": daily_count,
        "daily_revenue": daily_revenue,
        "total_revenue": total_sales_revenue
    }

# --- Dashboard Helpers ---
def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM reservations WHERE status != 'Checked-out'")
    total_bookings = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM rooms WHERE status = 'Available'")
    rooms_available = cursor.fetchone()[0]
    
    # Total Revenue should include Room costs + Sales
    cursor.execute("SELECT SUM(cost) FROM reservations WHERE pay_status = 'Paid'")
    res_revenue = cursor.fetchone()[0] or 0
    
    # Also add Instant payments from Sales (Room charges are already added to reservation cost)
    cursor.execute("SELECT SUM(total_cost) FROM sales WHERE payment_method = 'Instant'")
    sales_revenue = cursor.fetchone()[0] or 0
    
    total_revenue = res_revenue + sales_revenue
    
    cursor.execute("SELECT COUNT(*) FROM reservations WHERE check_out <= CURRENT_DATE AND status != 'Checked-out'")
    checkouts_today = cursor.fetchone()[0]
    
    conn.close()
    return {
        "total_bookings": f"{total_bookings:,}",
        "rooms_available": str(rooms_available),
        "checkouts_today": str(checkouts_today),
        "total_revenue": f"GH₵ {total_revenue:,.0f}"
    }

# Initialize the DB on import
init_db()
