import os
import sys
import json
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
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    import psycopg2
    from backend.core.config import settings

class ScraperRepository:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            try:
                from backend.core.config import settings
                self.db_url = settings.DATABASE_URL
            except:
                self.db_url = "postgresql://postgres.fenlzmyffahriefuljom:p6JmSE8wTDPZkkDS@aws-1-eu-west-2.pooler.supabase.com:6543/postgres"
    
    def _safe_log(self, message: str):
        try:
            encoding = sys.stdout.encoding or 'utf-8'
            print(str(message).encode(encoding, errors='replace').decode(encoding))
        except:
            print(message)

    def save_cars(self, cars: list, table_name: str = "cars"):
        if HAS_SQLALCHEMY:
            self._save_with_sqlalchemy(cars, table_name)
        else:
            self._save_with_psycopg2(cars, table_name)
            
        if table_name == "cars":
            try:
                import subprocess
                script_path = os.path.join(ROOT, "scrapers", "utils", "comparison_engine.py")
                # Run the export process in a detached or background manner so it doesn't block the scraper flow
                subprocess.Popen([sys.executable, script_path])
                self._safe_log("🚀 Auto-sync triggered: Synchronizing new 'cars' records to 'car_export'...")
            except Exception as e:
                self._safe_log(f"⚠️ Failed to auto-trigger car_export sync: {e}")

    def _save_with_sqlalchemy(self, cars: list, table_name: str):
        session = SessionLocal()
        try:
            for car in cars:
                # NUCLEAR FIX for Pydantic Types (HttpUrl, etc)
                if hasattr(car, 'model_dump_json'):
                    car_dict = json.loads(car.model_dump_json())
                else:
                    car_dict = car.model_dump() if hasattr(car, 'model_dump') else car
                
                car_url = str(car_dict.get('url', ''))
                
                # Dynamic insert using text() to support table_name
                query = text(f"""
                    INSERT INTO {table_name} (id, portal, brand, model, year, kilometrage, mileage, fuel, power, price, currency, country, location, url, source_url, images, vehicle_status, vehicle_status_check)
                    VALUES (:id, :portal, :brand, :model, :year, :kilometrage, :mileage, :fuel, :power, :price, :currency, :country, :location, :url, :source_url, :images, :vehicle_status, :vehicle_status_check)
                    ON CONFLICT (id) DO UPDATE SET
                        price = EXCLUDED.price,
                        mileage = EXCLUDED.mileage,
                        kilometrage = EXCLUDED.kilometrage,
                        fuel = EXCLUDED.fuel,
                        power = EXCLUDED.power,
                        location = EXCLUDED.location,
                        source_url = EXCLUDED.source_url,
                        images = EXCLUDED.images,
                        vehicle_status = EXCLUDED.vehicle_status,
                        vehicle_status_check = EXCLUDED.vehicle_status_check;
                """)
                
                # Ensure images is a list of strings
                images_list = car_dict.get('images', [])
                if not isinstance(images_list, list):
                    images_list = [str(images_list)] if images_list else []
                images_list = [str(img) for img in images_list]
                
                # CRITICAL: Pre-serialize to JSON string for Postgres JSONB column
                # This prevents SQLAlchemy from trying to pass it as a text array (text[])
                images_json = json.dumps(images_list)
                
                params = {
                    "id": car_url,
                    "portal": str(car_dict.get('portal')),
                    "brand": str(car_dict.get('brand')),
                    "model": str(car_dict.get('model')),
                    "year": int(car_dict.get('year', 2023)),
                    "kilometrage": int(car_dict.get('mileage', 0)),
                    "mileage": int(car_dict.get('mileage', 0)),
                    "fuel": str(car_dict.get('fuel')),
                    "power": car_dict.get('power'),
                    "price": float(car_dict.get('price', 0.0)),
                    "currency": str(car_dict.get('currency', 'EUR')),
                    "country": str(car_dict.get('country', 'España')),
                    "location": str(car_dict.get('location') or 'Desconocido'),
                    "url": car_url,
                    "source_url": str(car_dict.get('source_url') or car_url),
                    "images": images_json,  # Pass as string!
                    "vehicle_status": str(car_dict.get('vehicle_status', 'Dudoso')),
                    "vehicle_status_check": str(car_dict.get('vehicle_status_check', 'Dudoso'))
                }
                session.execute(query, params)
            
            session.commit()
            self._safe_log(f"Successfully saved {len(cars)} cars to '{table_name}' using SessionLocal.")
        except Exception as e:
            session.rollback()
            self._safe_log(f"SQLAlchemy Error saving to {table_name}: {e}")
            raise e
        finally:
            session.close()

    def _save_with_psycopg2(self, cars: list, table_name: str):
        conn = None
        try:
            import psycopg2
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            for car in cars:
                if hasattr(car, 'model_dump_json'):
                    car_dict = json.loads(car.model_dump_json())
                else:
                    car_dict = car.model_dump() if hasattr(car, 'model_dump') else car
                
                car_url = str(car_dict.get('url', ''))
                
                query = f"""
                    INSERT INTO {table_name} (id, portal, brand, model, year, kilometrage, mileage, fuel, power, price, currency, country, location, url, source_url, images, vehicle_status, vehicle_status_check)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        price = EXCLUDED.price,
                        mileage = EXCLUDED.mileage,
                        kilometrage = EXCLUDED.kilometrage,
                        fuel = EXCLUDED.fuel,
                        power = EXCLUDED.power,
                        location = EXCLUDED.location,
                        source_url = EXCLUDED.source_url,
                        images = EXCLUDED.images,
                        vehicle_status = EXCLUDED.vehicle_status,
                        vehicle_status_check = EXCLUDED.vehicle_status_check;
                """
                
                images_list = car_dict.get('images', [])
                if not isinstance(images_list, list):
                    images_list = [str(images_list)] if images_list else []
                images_list = [str(img) for img in images_list]

                cur.execute(query, (
                    car_url, car_dict.get('portal'), car_dict.get('brand'), car_dict.get('model'), 
                    car_dict.get('year'), car_dict.get('mileage'), car_dict.get('mileage'), 
                    car_dict.get('fuel'), car_dict.get('power'), car_dict.get('price'), 
                    car_dict.get('currency'), car_dict.get('country'), 
                    car_dict.get('location', 'Desconocido'), car_url,
                    str(car_dict.get('source_url') or car_url),
                    json.dumps(images_list),
                    str(car_dict.get('vehicle_status', 'Dudoso')),
                    str(car_dict.get('vehicle_status_check', 'Dudoso'))
                ))
            conn.commit()
            self._safe_log(f"Successfully saved {len(cars)} cars to '{table_name}' using psycopg2.")
        except Exception as e:
            if conn: conn.rollback()
            self._safe_log(f"Psycopg2 Error saving to {table_name}: {e}")
            raise e
        finally:
            if conn: conn.close()

    def cleanup_invalid_cars(self, table_name: str = "cars") -> int:
        """Removes cars that are not Mercedes Vito, Sprinter, or Citan."""
        query_sql = f"""
            DELETE FROM {table_name}
            WHERE LOWER(brand) NOT LIKE '%mercedes%'
            OR (
                LOWER(model) NOT LIKE '%vito%'
                AND LOWER(model) NOT LIKE '%sprinter%'
                AND LOWER(model) NOT LIKE '%citan%'
            );
        """
        deleted_count = 0
        
        if HAS_SQLALCHEMY:
            session = SessionLocal()
            try:
                result = session.execute(text(query_sql))
                deleted_count = result.rowcount
                session.commit()
                self._safe_log(f"Cleanup: Removed {deleted_count} invalid records from '{table_name}' using SQLAlchemy.")
            except Exception as e:
                session.rollback()
                self._safe_log(f"Cleanup Error (SQLAlchemy): {e}")
            finally:
                session.close()
        else:
            conn = None
            try:
                import psycopg2
                conn = psycopg2.connect(self.db_url)
                cur = conn.cursor()
                cur.execute(query_sql)
                deleted_count = cur.rowcount
                conn.commit()
                self._safe_log(f"Cleanup: Removed {deleted_count} invalid records from '{table_name}' using psycopg2.")
            except Exception as e:
                if conn: conn.rollback()
                self._safe_log(f"Cleanup Error (psycopg2): {e}")
            finally:
                if conn: conn.close()
        
        return deleted_count
