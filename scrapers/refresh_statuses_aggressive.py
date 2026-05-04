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

def refresh_status_aggressive():
    print(f"Connecting to database for AGGRESSIVE refresh...")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("Analyzing 'cars' table with mandatory cleanliness rule...")
        res = conn.execute(text("SELECT id, brand, model, url FROM cars"))
        updates = []
        for r in res.mappings():
            # In existing DB, we only have brand, model, url. 
            # We don't have the 'specs' (badges) unless we re-scrape.
            # So we check if the URL or title/brand contains ANY hint of damage or LACKS "unfallfrei"/"sin accidentes"
            text_to_check = f"{r['brand']} {r['model']} {r['url']}".lower()
            
            is_explicitly_clean = re.search(r'\b(unfallfrei|kein unfallschaden|sin accidentes|libre de accidentes)\b', text_to_check)
            has_damage_keywords = any(re.search(kw, text_to_check, re.IGNORECASE) for kw in ACCIDENT_KEYWORDS)
            
            if has_damage_keywords:
                status = "Descartado"
            elif not is_explicitly_clean:
                # If it doesn't say it's clean, we mark as Descartado/Dudoso
                # Since the user says many are damaged, we'll be very strict
                status = "Descartado" 
            else:
                status = "Sin accidentes"
                
            updates.append({"id": r['id'], "status": status})
        
        print(f"Updating {len(updates)} records...")
        for up in updates:
            conn.execute(text("UPDATE cars SET vehicle_status = :status WHERE id = :id"), up)
        
        conn.commit()
        print(f"Successfully refreshed records. Purguing car_export...")
        
        # Now delete anything from car_export that is NOT "Sin accidentes"
        conn.execute(text("DELETE FROM car_export WHERE vehicle_status != 'Sin accidentes'"))
        conn.commit()
        print("car_export table purged of non-pristine vehicles.")

if __name__ == "__main__":
    refresh_status_aggressive()
