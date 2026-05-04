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
from scrapers.portal_scrapers.mobile_de import ACCIDENT_KEYWORDS

def refresh_status_strict_v2():
    print(f"Connecting to database for STRICT V2 refresh...")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("Truncating car_export and favorites to ensure no damaged cars remain...")
        # We use CASCADE to handle foreign keys
        conn.execute(text("TRUNCATE TABLE car_export CASCADE"))
        conn.commit()
        
        print("Analyzing 'cars' table (IGNORING FIXED URLs)...")
        res = conn.execute(text("SELECT id, brand, model, url FROM cars"))
        updates = []
        for r in res.mappings():
            # Marcamos TODO lo antiguo como "Dudoso" 
            status = "Dudoso" 
            
            text_to_check = f"{r['brand']} {r['model']}".lower()
            if any(re.search(kw, text_to_check, re.IGNORECASE) for kw in ACCIDENT_KEYWORDS):
                status = "Descartado"
                
            updates.append({"id": r['id'], "status": status})
        
        print(f"Updating {len(updates)} records to 'Dudoso' or 'Descartado'...")
        for up in updates:
            conn.execute(text("UPDATE cars SET vehicle_status = :status WHERE id = :id"), up)
        
        conn.commit()
        print("Database cleaned. Dashboard is now EMPTY.")

if __name__ == "__main__":
    refresh_status_strict_v2()
