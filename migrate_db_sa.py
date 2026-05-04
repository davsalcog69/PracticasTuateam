import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.join(ROOT, "backend")
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from core.database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE cars ADD COLUMN vehicle_status_check VARCHAR NOT NULL DEFAULT 'Dudoso'"))
            print("Added vehicle_status_check to cars table.")
        except Exception as e:
            print(f"Skipped cars: {e}")

        try:
            conn.execute(text("ALTER TABLE car_export ADD COLUMN vehicle_status_check VARCHAR NOT NULL DEFAULT 'Dudoso'"))
            print("Added vehicle_status_check to car_export table.")
        except Exception as e:
            print(f"Skipped car_export: {e}")
            
        conn.commit()

if __name__ == "__main__":
    migrate()
