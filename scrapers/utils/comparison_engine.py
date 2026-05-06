import os
import sys
import re
import difflib
import json
import statistics
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
        
        # Filtro estricto por tipo de carrocería (Touring/Familiar vs Berlina)
        body_types = ["touring", "estate", "familiar", "variant", "avant"]
        c1_is_estate = any(b in c1 for b in body_types)
        c2_is_estate = any(b in c2 for b in body_types)
        if c1_is_estate != c2_is_estate:
            return False # No mezclar berlinas con familiares
            
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

    def calculate_market_median(self, comparables: List[Dict[str, Any]]) -> float:
        if not comparables:
            return 0.0
            
        prices = [c['price_eur'] for c in comparables if c.get('price_eur', 0) > 0]
        if not prices:
            return 0.0
            
        # ELIMINAR OUTLIERS (Truncamiento del 15% superior e inferior si hay suficientes datos)
        prices.sort()
        n = len(prices)
        if n >= 5:
            trim_count = int(n * 0.15) # 15% de cada lado
            if trim_count > 0:
                prices = prices[trim_count:-trim_count]
                
        # Usar mediana en vez de media para mayor robustez
        return statistics.median(prices)
        
    def calculate_equipment_adjustment(self, car_dict: Dict[str, Any]) -> float:
        adjustment = 0.0
        text_to_check = f"{car_dict.get('brand', '')} {car_dict.get('model', '')}".lower()
        
        # Ajustes inteligentes por equipamiento premium
        premium_keywords = ["m sport", "s line", "amg line", "r-line", "r line"]
        if any(kw in text_to_check for kw in premium_keywords):
            adjustment += 1500.0 # Sumar valor al precio de venta estimado
            
        return adjustment

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
            vehicle_status_check TEXT,
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
            roi_percentage DOUBLE PRECISION,
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
                
                # --- FILTRO DE ESTADO VEHÍCULO (CRÍTICO) ---
                # A petición del usuario (Modo Debug/Menos agresivo): Dejar pasar OK y Dudoso
                # SOLO "Descartado" se bloquea
                vehicle_status_check = car_dict.get('vehicle_status_check', 'Dudoso')
                if vehicle_status_check == "Descartado":
                    logger.info(f"Ocultando coche {car_dict['id']} por estado de chequeo: {vehicle_status_check}")
                    # Si ya estaba en export, lo borramos
                    session.execute(text("DELETE FROM car_export WHERE id = :id"), {"id": car_dict['id']})
                    continue
                # LISTA NEGRA COMPLETA (Alemán, Español, Inglés)
                accident_keywords = [
                    # ACCIDENTES (DIRECTO)
                    r'unfall', r'unfallschaden', r'unfallfahrzeug', r'schwerer unfall', r'totalschaden', r'unfallwagen', 
                    r'frontschaden', r'heckschaden', r'seitenschaden',
                    r'accidente', r'siniestro', r'coche accidentado', r'golpe frontal', r'golpe trasero', r'golpe lateral', r'siniestro total',
                    r'accident', r'accident damage', r'total loss', r'crash damage', r'front damage', r'rear damage', r'side damage',
                    
                    # DAÑOS GENERALES
                    r'beschädigt', r'schaden', r'vorschaden', r'altschaden', r'beschädigungen', r'mängel',
                    r'dañado', r'daños', r'daños previos', r'defectos', r'desperfectos',
                    r'damaged', r'damage', r'previous damage', r'defects', r'issues',
                    
                    # DAÑOS MECÁNICOS
                    r'motorschaden', r'getriebeschaden', r'turboschaden', r'kupplung defekt', r'motor defekt', r'getriebe defekt',
                    r'nicht fahrbereit', r'bedingt fahrbereit',
                    r'motor roto', r'avería', r'caja de cambios rota', r'embrague roto', r'no arranca', r'no funciona', r'no circula',
                    r'engine damage', r'engine failure', r'gearbox damage', r'transmission issue', r'not working', r'not drivable', r'broken',
                    
                    # COCHES PROBLEMÁTICOS
                    r'bastlerfahrzeug', r'exportfahrzeug', r'händlerexport', r'ohne garantie', r'nur für export', r'zum ausschlachten',
                    r'para piezas', r'para exportación', r'sin garantía', r'solo exportación', r'para desguace',
                    r'for parts', r'export only', r'no warranty', r'salvage', r'scrap',
                    
                    # REPARACIONES / SOSPECHOSO
                    r'repariert', r'instandgesetzt', r'nachlackiert', r'neu lackiert', r'lackschaden', r'karosserieschaden', 
                    r'rahmenschaden', r'instandsetzung',
                    r'reparado', r'repintado', r'pintura nueva', r'daño de carrocería', r'daño estructural',
                    r'repaired', r'repainted', r'body repair', r'frame damage', r'structural damage',
                    
                    # DESGASTE / ESTADO MALO
                    r'stark gebraucht', r'verschlissen', r'abgenutzt',
                    r'muy usado', r'desgastado', r'desgaste alto',
                    r'heavily used', r'worn'
                    
                    # EXPRESIONES ENGAÑOSAS
                    r'minor defects', r'cosmetic issues'
                ]
                # We check the brand, model and URL as they might contain these keywords
                text_to_check = f"{car_dict.get('brand', '')} {car_dict.get('model', '')} {car_dict.get('url', '')}".lower()
                if any(re.search(kw, text_to_check) for kw in accident_keywords):
                    logger.info(f"Skipping car {car_dict['id']} due to accident keyword match.")
                    # Ensure it's removed from export if it was there
                    session.execute(text("DELETE FROM car_export WHERE id = :id"), {"id": car_dict['id']})
                    continue
                    
                # 1. Prices
                car_dict['price_eur'] = self.get_price_eur(car_dict['price'], car_dict.get('currency', 'EUR'))
                comparables = self.find_comparables(car_dict, session)
                
                avg_price_spain = 0
                profit = 0
                roi_pct = 0.0
                
                costs = self.calculate_import_costs(car_dict['price_eur'])
                final_landing_price = car_dict['price_eur'] + costs['total_import_cost']
                
                if comparables:
                    # Usar mediana y eliminar outliers
                    base_median_price = self.calculate_market_median(comparables)
                    
                    # Ajustes inteligentes (Equipamiento)
                    equipment_adj = self.calculate_equipment_adjustment(car_dict)
                    avg_price_spain = base_median_price + equipment_adj
                    
                    profit = avg_price_spain - final_landing_price
                    
                    # ROI = (precio_venta_estimado - precio_compra - costes) / precio_compra
                    if car_dict['price_eur'] > 0:
                        roi_pct = ((avg_price_spain - final_landing_price) / final_landing_price) * 100.0
                
                # 3. Filter (Strict minimum profitability: 500€)
                if profit < 500:
                    # Remove explicitly from car_export if it was previously exported
                    session.execute(text("DELETE FROM car_export WHERE id = :id"), {"id": car_dict['id']})
                    logger.info(f"Skipping or deleting car {car_dict['id']} due to low profit ({profit}€).")
                    continue
                
                # 5. FIXED LINKS BY MODEL (USER REQUEST)
                # Instead of individual links, we use the search results link for the model
                model_upper = str(car_dict['model']).upper()
                if "CITAN" in model_upper:
                    fixed_url = "https://www.mobile.de/es/veh%C3%ADculos/buscar.html?sb=p&od=up&vc=Car&fr=2023&ms=17200%3B224&st=DEALER&s=Car&ref=srpHead"
                elif "VITO" in model_upper:
                    fixed_url = "https://www.mobile.de/es/veh%C3%ADculos/buscar.html?sb=p&od=up&vc=Car&fr=2023&st=DEALER&ms=17200%3B125&s=Car&ref=srpHead"
                elif "SPRINTER" in model_upper:
                    fixed_url = "https://www.mobile.de/es/veh%C3%ADculos/buscar.html?sb=p&od=up&vc=Car&fr=2023&ms=17200%3B116&st=DEALER&s=Car&ref=srpHead"
                elif "SERIE 3" in model_upper:
                    fixed_url = "https://www.mobile.de/es/veh%C3%ADculos/buscar.html?c=EstateCar&c=Limousine&fr=2019%3A2022&ft=PETROL&ml=%3A80000&ms=3500%3B10%3B%3B%3B&od=up&p=%3A35000&s=Car&sb=p&st=DEALER&tr=AUTOMATIC_GEAR&ud=0&vc=Car"
                elif "A4" in model_upper:
                    fixed_url = "https://www.mobile.de/es/veh%C3%ADculos/buscar.html?c=EstateCar&c=Limousine&fr=2019%3A2022&ml=%3A75000&ms=1900%3B9%3B%3B%3B&od=up&p=%3A32000&s=Car&sb=p&st=DEALER&tr=AUTOMATIC_GEAR&ud=0&vc=Car"
                elif "GOLF GTI" in model_upper:
                    fixed_url = "https://www.mobile.de/es/veh%C3%ADculos/buscar.html?fr=2020%3A2023&ft=PETROL&ml=%3A60000&ms=25200%3B14%3B%3B%3B&od=up&p=%3A28000&pw=180%3A&s=Car&sb=p&ud=0&vc=Car"
                elif "GOLF R" in model_upper:
                    fixed_url = "https://www.mobile.de/es/veh%C3%ADculos/buscar.html?fr=2020%3A2023&ft=PETROL&ml=%3A60000&ms=25200%3B14%3B%3B%3B&od=up&p=%3A35000&pw=220%3A&s=Car&sb=p&ud=0&vc=Car"
                else:
                    fixed_url = car_dict['url'] # Fallback
                
                # 4. Save to car_export using RAW SQL UPSERT to avoid UniqueViolation
                export_params = {
                    "id": car_dict['id'],
                    "portal": car_dict['portal'],
                    "brand": car_dict['brand'],
                    "model": car_dict['model'],
                    "vehicle_status": car_dict.get('vehicle_status', 'Gebrauchtfahrzeug'),
                    "vehicle_status_check": car_dict.get('vehicle_status_check', 'OK'),
                    "year": car_dict['year'],
                    "mileage": car_dict['mileage'],
                    "fuel": car_dict['fuel'],
                    "power": car_dict.get('power'),
                    "price": car_dict['price'],
                    "currency": car_dict['currency'],
                    "country": car_dict['country'],
                    "location": car_dict['location'],
                    "url": fixed_url,
                    "images": json.dumps(images) if not isinstance(images, str) else images,
                    "price_eur": car_dict['price_eur'],
                    "price_spain_avg": round(avg_price_spain, 2),
                    "transport_cost": costs['transport'],
                    "itv_cost": costs['itv'],
                    "registration_cost": costs['registration'],
                    "gestor_cost": costs['gestor'],
                    "total_import_cost": costs['total_import_cost'],
                    "final_price": round(final_landing_price, 2),
                    "estimated_profit": round(profit, 2),
                    "roi_percentage": round(roi_pct, 2)
                }

                upsert_query = text("""
                    INSERT INTO car_export (
                        id, portal, brand, model, vehicle_status, vehicle_status_check, year, mileage, fuel, power,
                        price, currency, country, location, url, images,
                        price_eur, price_spain_avg, transport_cost, itv_cost, registration_cost,
                        gestor_cost, total_import_cost, final_price, estimated_profit, roi_percentage
                    ) VALUES (
                        :id, :portal, :brand, :model, :vehicle_status, :vehicle_status_check, :year, :mileage, :fuel, :power,
                        :price, :currency, :country, :location, :url, CAST(:images AS jsonb),
                        :price_eur, :price_spain_avg, :transport_cost, :itv_cost, :registration_cost,
                        :gestor_cost, :total_import_cost, :final_price, :estimated_profit, :roi_percentage
                    ) ON CONFLICT (id) DO UPDATE SET
                        vehicle_status = EXCLUDED.vehicle_status,
                        vehicle_status_check = EXCLUDED.vehicle_status_check,
                        price = EXCLUDED.price,
                        images = EXCLUDED.images,
                        price_eur = EXCLUDED.price_eur,
                        price_spain_avg = EXCLUDED.price_spain_avg,
                        final_price = EXCLUDED.final_price,
                        estimated_profit = EXCLUDED.estimated_profit,
                        roi_percentage = EXCLUDED.roi_percentage,
                        url = EXCLUDED.url,
                        mileage = EXCLUDED.mileage
                """)
                
                session.execute(upsert_query, export_params)
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
