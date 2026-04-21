import os
import sys
import re
import difflib
import json
from typing import List, Dict, Any, Optional, Set
import logging
from sqlalchemy import text

# --- PATH FIX TO FIND BACKEND ---
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND_ROOT = os.path.join(ROOT, "backend")

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

try:
    from backend.core.database import SessionLocal
    HAS_DB = True
except ImportError:
    HAS_DB = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ComparisonEngine")

class ComparisonEngine:
    def __init__(self, db_url: str = None):
        self.db_url = db_url
        self.exchange_rates = {
            "AED": 0.254, 
            "USD": 0.923, 
            "EUR": 1.0,
            "SAR": 0.246 
        }

    def clean_text(self, text: str) -> str:
        if not text: return ""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        words = text.split()
        seen = set()
        unique_words = []
        for w in words:
            if w not in seen:
                unique_words.append(w)
                seen.add(w)
        return " ".join(unique_words)

    def is_match(self, model1: str, model2: str, threshold: float = 0.7) -> bool:
        c1 = self.clean_text(model1)
        c2 = self.clean_text(model2)
        if not c1 or not c2: return False
        if c1 in c2 or c2 in c1: return True
        similarity = difflib.SequenceMatcher(None, c1, c2).ratio()
        return similarity >= threshold

    def get_price_eur(self, price: float, currency: str) -> float:
        rate = self.exchange_rates.get(str(currency).upper(), 1.0)
        return round(float(price) * rate, 2)

    def find_comparables(self, intl_car: Dict[str, Any], session) -> List[Dict[str, Any]]:
        brand = intl_car.get('brand')
        model = intl_car.get('model')
        year = intl_car.get('year')
        mileage = intl_car.get('mileage') or intl_car.get('kilometrage') or 0
        
        if not brand or not model: return []

        query = text("""
            SELECT * FROM cars 
            WHERE portal = 'coches.net'
            AND (LOWER(brand) LIKE '%' || LOWER(:brand) || '%' OR LOWER(:brand) LIKE '%' || LOWER(brand) || '%')
            AND year BETWEEN :y_min AND :y_max
        """)
        
        results = session.execute(query, {
            "brand": brand,
            "y_min": year - 2,
            "y_max": year + 2
        })
        
        comparables = []
        for row in results:
            match = dict(row._mapping)
            if self.is_match(model, match.get('model')):
                match['price_eur'] = self.get_price_eur(match['price'], match.get('currency', 'EUR'))
                comparables.append(match)
                
        return comparables

    def calculate_import_costs(self, price_eur: float) -> Dict[str, Any]:
        # Based on user business logic (simplified)
        transport = 1500.0 if price_eur > 0 else 0 # From Germany/EU
        itv = 150.0
        registration = 300.0
        gestor = 250.0
        
        # Simplified Taxes for EU -> ES (No Arancel if EU, but user might want it)
        # Mobile.de is typically EU. UAE (dubicars) had 10%.
        # Let's keep it simple: 2500 fixed as seen in CarDetailModal
        total_costs = 2500.0
        
        return {
            "transport": 1500.0,
            "itv": itv,
            "registration": registration,
            "gestor": gestor,
            "total_import_cost": total_costs
        }

    async def ensure_car_export_table(self, session):
        # We use migrate_db_final.py for this, but let's be safe
        query = text("""
        CREATE TABLE IF NOT EXISTS car_export (
            id TEXT PRIMARY KEY,
            portal TEXT,
            brand TEXT,
            model TEXT,
            year INTEGER,
            mileage INTEGER,
            fuel TEXT,
            power INTEGER,
            price DOUBLE PRECISION,
            currency TEXT,
            country TEXT,
            location TEXT,
            url TEXT,
            images JSONB DEFAULT '[]'::jsonb,
            price_eur DOUBLE PRECISION,
            price_spain_avg DOUBLE PRECISION,
            transport_cost DOUBLE PRECISION,
            import_tax DOUBLE PRECISION,
            itv_cost DOUBLE PRECISION,
            registration_cost DOUBLE PRECISION,
            gestor_cost DOUBLE PRECISION,
            total_import_cost DOUBLE PRECISION,
            final_price DOUBLE PRECISION,
            estimated_profit DOUBLE PRECISION,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)
        session.execute(query)
        session.commit()

    async def run_export_process(self):
        if not HAS_DB:
             logger.error("No database connection available.")
             return

        session = SessionLocal()
        try:
            await self.ensure_car_export_table(session)
            
            # Fetch mobile.de cars
            intl_cars = session.execute(text("SELECT * FROM cars WHERE portal != 'coches.net'")).mappings().all()
            logger.info(f"Processing {len(intl_cars)} international records for ROI analysis...")
            
            inserted_count = 0
            for row in intl_cars:
                car_dict = dict(row)
                
                # Format images correctly (ensure it's a list)
                images = car_dict.get('images', [])
                if isinstance(images, str):
                    try:
                        images = json.loads(images)
                    except:
                        images = []
                elif images is None:
                    images = []
                    
                # NEW: Skip cars with 0 images as per user request
                if not images:
                    logger.info(f"Skipping car {car_dict['id']} because it has 0 images.")
                    continue
                    
                # 1. Prices
                car_dict['price_eur'] = self.get_price_eur(car_dict['price'], car_dict.get('currency', 'EUR'))
                comparables = self.find_comparables(car_dict, session)
                
                avg_price_spain = 0
                profit = 0
                
                if comparables:
                    avg_price_spain = sum(c['price_eur'] for c in comparables) / len(comparables)
                    # 2. Costs
                    costs = self.calculate_import_costs(car_dict['price_eur'])
                    final_landing_price = car_dict['price_eur'] + costs['total_import_cost']
                    profit = avg_price_spain - final_landing_price
                else:
                    # Default costs if no comparables
                    costs = self.calculate_import_costs(car_dict['price_eur'])
                    final_landing_price = car_dict['price_eur'] + costs['total_import_cost']
                    profit = 0 # No match, no ROI calculated
                
                # 3. Filter (Strict minimum profitability: 500€)
                if profit < 500:
                    # Remove explicitly from car_export if it was previously exported
                    session.execute(text("DELETE FROM car_export WHERE id = :id"), {"id": car_dict['id']})
                    logger.info(f"Skipping or deleting car {car_dict['id']} due to low profit ({profit}€).")
                    continue
                
                # 4. Save to car_export using ORM model
                from backend.models.car_export import CarExport
                
                # Create or update record
                car_export = session.get(CarExport, car_dict['id'])
                if not car_export:
                    car_export = CarExport(id=car_dict['id'])
                    session.add(car_export)
                
                car_export.portal = car_dict['portal']
                car_export.brand = car_dict['brand']
                car_export.model = car_dict['model']
                car_export.year = car_dict['year']
                car_export.mileage = car_dict['mileage']
                car_export.fuel = car_dict['fuel']
                car_export.power = car_dict['power']
                car_export.price = car_dict['price']
                car_export.currency = car_dict['currency']
                car_export.country = car_dict['country']
                car_export.location = car_dict['location']
                # 5. FIXED LINKS BY MODEL (USER REQUEST)
                # Instead of individual links, we use the search results link for the model
                model_upper = str(car_dict['model']).upper()
                if "CITAN" in model_upper:
                    fixed_url = "https://www.mobile.de/es/veh%C3%ADculos/buscar.html?sb=p&od=up&vc=Car&fr=2023&ms=17200%3B224&st=DEALER&s=Car&ref=srpHead"
                elif "VITO" in model_upper:
                    fixed_url = "https://www.mobile.de/es/veh%C3%ADculos/buscar.html?sb=p&od=up&vc=Car&fr=2023&st=DEALER&ms=17200%3B125&s=Car&ref=srpHead"
                elif "SPRINTER" in model_upper:
                    fixed_url = "https://www.mobile.de/es/veh%C3%ADculos/buscar.html?sb=p&od=up&vc=Car&fr=2023&ms=17200%3B116&st=DEALER&s=Car&ref=srpHead"
                else:
                    fixed_url = car_dict['url'] # Fallback
                
                car_export.url = fixed_url
                car_export.source_url = fixed_url # Keep both consistent for the UI
                car_export.images = images
                car_export.price_eur = car_dict['price_eur']
                car_export.price_spain_avg = round(avg_price_spain, 2)
                car_export.transport_cost = costs['transport']
                car_export.itv_cost = costs['itv']
                car_export.registration_cost = costs['registration']
                car_export.gestor_cost = costs['gestor']
                car_export.total_import_cost = costs['total_import_cost']
                car_export.final_price = round(final_landing_price, 2)
                car_export.estimated_profit = round(profit, 2)
                
                inserted_count += 1
            
            session.commit()
            logger.info(f"ROI analysis complete: {inserted_count} profitable cars exported.")
        except Exception as e:
            session.rollback()
            logger.error(f"Error: {e}")
            raise e
        finally:
            session.close()

if __name__ == "__main__":
    from backend.core.config import settings
    engine = ComparisonEngine(settings.DATABASE_URL)
    import asyncio
    asyncio.run(engine.run_export_process())
