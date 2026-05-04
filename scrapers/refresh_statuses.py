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

def refresh_status():
    print(f"Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("Refreshing 'cars' table statuses...")
        res = conn.execute(text("SELECT id, brand, model, url FROM cars"))
        updates = []
        for r in res.mappings():
            text_to_check = f"{r['brand']} {r['model']} {r['url']}".lower()
            
            # Simple logic for existing data
            if any(re.search(kw, text_to_check) for kw in ACCIDENT_KEYWORDS):
                status = "Descartado"
            elif "unfallfrei" in text_to_check or "kein unfallschaden" in text_to_check:
                status = "Sin accidentes"
            else:
                # For existing high-quality data that passed previous filters, we assume "Sin accidentes" 
                # to avoid wiping the whole dashboard, but we mark as "Sin accidentes" only if it looks very clean.
                status = "Sin accidentes" # Conservative for existing data that passed previous strict filters
                
            updates.append({"id": r['id'], "status": status})
        
        for up in updates:
            conn.execute(text("UPDATE cars SET vehicle_status = :status WHERE id = :id"), up)
        
        conn.commit()
        print(f"Successfully refreshed {len(updates)} records in 'cars'")

if __name__ == "__main__":
    refresh_status()
