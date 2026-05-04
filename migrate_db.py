import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'backend', 'database', 'marketplace.db')
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}, trying different path...")
    # Maybe it's in the root?
    db_path = os.path.join(os.path.dirname(__file__), 'marketplace.db')

print(f"Using database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column exists in cars table
    cursor.execute("PRAGMA table_info(cars)")
    columns = [info[1] for info in cursor.fetchall()]
    if "vehicle_status_check" not in columns:
        cursor.execute("ALTER TABLE cars ADD COLUMN vehicle_status_check TEXT NOT NULL DEFAULT 'Dudoso'")
        print("Added vehicle_status_check to cars table.")
    else:
        print("vehicle_status_check already exists in cars table.")
        
    # Check if column exists in car_export table
    cursor.execute("PRAGMA table_info(car_export)")
    columns = [info[1] for info in cursor.fetchall()]
    if "vehicle_status_check" not in columns:
        cursor.execute("ALTER TABLE car_export ADD COLUMN vehicle_status_check TEXT NOT NULL DEFAULT 'Dudoso'")
        print("Added vehicle_status_check to car_export table.")
    else:
        print("vehicle_status_check already exists in car_export table.")
        
    conn.commit()
    conn.close()
    print("Migration successful.")
except Exception as e:
    print(f"Error during migration: {e}")
