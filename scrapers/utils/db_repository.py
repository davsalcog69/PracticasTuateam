import psycopg2
from psycopg2.extras import execute_values
import os
from datetime import datetime
from base.schemas import CarAdSchema

class ScraperRepository:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/car_import_ai")
    
    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def save_cars(self, cars: list[CarAdSchema]):
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            for car in cars:
                # 1. Insert or ignore into cars (duplicate prevention by URL)
                cur.execute("""
                    INSERT INTO cars (id, portal, brand, model, version, year, kilometrage, fuel, power, price, currency, location, url, scraped_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO UPDATE SET
                        price = EXCLUDED.price,
                        kilometrage = EXCLUDED.kilometrage,
                        scraped_at = EXCLUDED.scraped_at
                    RETURNING id;
                """, (
                    str(car.url), # Or a UUID if id is primary key and not URL
                    car.portal, car.brand, car.model, car.version, car.year, 
                    car.kilometrage, car.fuel, car.power, car.price, car.currency, 
                    car.location, str(car.url), car.scraped_at
                ))
                
                car_id = cur.fetchone()[0]
                
                # 2. Insert images
                if car.images:
                    image_data = [(car_id, str(img_url)) for img_url in car.images]
                    execute_values(cur, """
                        INSERT INTO car_images (car_id, image_url) VALUES %s
                        ON CONFLICT DO NOTHING;
                    """, image_data)
            
            conn.commit()
            print(f"Successfully saved {len(cars)} cars to the database.")
        except Exception as e:
            conn.rollback()
            print(f"Error saving cars to DB: {e}")
        finally:
            cur.close()
            conn.close()
