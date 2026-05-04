import sys
import os
import re
from sqlalchemy import create_engine, text

# --- PATH FIX ---
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_ROOT = os.path.join(ROOT, "backend")
if ROOT not in sys.path: sys.path.insert(0, ROOT)
if BACKEND_ROOT not in sys.path: sys.path.insert(0, BACKEND_ROOT)

from backend.core.config import settings

def check_db():
    db_url = settings.DATABASE_URL
    print(f"Connecting to database...")
    engine = create_engine(db_url)
    
    keywords = [
        r'unfall', r'damage', r'repariert', r'crash', r'salvage',
        r'accidente', r'daño', r'siniestro', r'reparado', r'golpe', r'avería',
        r'hagelschaden', r'totalschaden', r'rahmen', r'beschädigt', 
        r'motorschaden', r'getriebeschaden', r'unfaller'
    ]
    
    with engine.connect() as conn:
        print("Checking 'cars' table...")
        res = conn.execute(text("SELECT id, brand, model, year, url FROM cars"))
        count = 0
        for r in res.mappings():
            text_to_check = f"{r['brand']} {r['model']} {r['url']}".lower()
            if any(re.search(kw, text_to_check) for kw in keywords):
                print(f"MATCH in cars: {r['brand']} {r['model']} ({r['year']}) - {r['url']}")
                count += 1
        print(f"Total matches in 'cars': {count}")

        print("\nChecking 'car_export' table...")
        try:
            res = conn.execute(text("SELECT id, brand, model, year, url FROM car_export"))
            count = 0
            for r in res.mappings():
                text_to_check = f"{r['brand']} {r['model']} {r['url']}".lower()
                if any(re.search(kw, text_to_check) for kw in keywords):
                    print(f"MATCH in car_export: {r['brand']} {r['model']} ({r['year']}) - {r['url']}")
                    count += 1
            print(f"Total matches in 'car_export': {count}")
        except Exception as e:
            print(f"Error checking car_export: {e}")

if __name__ == "__main__":
    check_db()
