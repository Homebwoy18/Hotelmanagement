import sqlite3
import os

# Database name from your database.py
DB_NAME = "hotel_management.db"

def reset_database():
    if not os.path.exists(DB_NAME):
        print(f"Error: Database file '{DB_NAME}' not found.")
        return

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # List of tables to clear
        tables = ['sales', 'reservations', 'rooms', 'inventory_items']
        
        print("Starting Database Reset...")
        
        # 1. Clear data from tables
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
                print(f" [✓] Cleared table: {table}")
            except sqlite3.OperationalError as e:
                print(f" [!] Skipping table {table}: {e}")
        
        # 2. Reset the ID counters (Auto-increments)
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('sales', 'reservations', 'rooms', 'inventory_items')")
        print(" [✓] ID counters reset.")
        
        conn.commit()
        conn.close()
        print("\nSUCCESS: All data has been cleared. Your application is now fresh and empty!")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")

if __name__ == "__main__":
    confirm = input("WARNING: This will delete ALL bookings, rooms, and sales data.\nAre you sure you want to proceed? (yes/no): ")
    if confirm.lower() == 'yes':
        reset_database()
    else:
        print("Reset cancelled.")
