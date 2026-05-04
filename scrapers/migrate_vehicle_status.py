import sys
import os
from sqlalchemy import create_engine, text

# --- PATH FIX ---
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_ROOT = os.path.join(ROOT, "backend")
if ROOT not in sys.path: sys.path.insert(0, ROOT)
if BACKEND_ROOT not in sys.path: sys.path.insert(0, BACKEND_ROOT)

from backend.core.config import settings

def migrate():
    db_url = settings.DATABASE_URL
    print(f"Connecting to database for migration...")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        # Add vehicle_status to cars
        try:
            print("Adding vehicle_status to 'cars' table...")
            conn.execute(text("ALTER TABLE cars ADD COLUMN vehicle_status VARCHAR DEFAULT 'Dudoso' NOT NULL"))
            conn.commit()
            print("Successfully added vehicle_status to 'cars'")
        except Exception as e:
            print(f"Could not add to 'cars' (maybe already exists?): {e}")

        # Add vehicle_status to car_export
        try:
            print("Adding vehicle_status to 'car_export' table...")
            conn.execute(text("ALTER TABLE car_export ADD COLUMN vehicle_status VARCHAR DEFAULT 'Dudoso' NOT NULL"))
            conn.commit()
            print("Successfully added vehicle_status to 'car_export'")
        except Exception as e:
            print(f"Could not add to 'car_export' (maybe already exists?): {e}")

if __name__ == "__main__":
    migrate()
