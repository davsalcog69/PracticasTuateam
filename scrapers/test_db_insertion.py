import os
import sys
import json
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

# ROOT fix
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def test_insertion():
    try:
        from backend.core.config import settings
        from backend.core.database import SessionLocal
        
        print(f"Connecting to: {settings.DATABASE_URL.split('@')[-1]}") # Log host safely
        
        db = SessionLocal()
        
        test_id = "test_insertion_id_123"
        print(f"Attempting to insert test record into 'dubicars' table...")
        
        query = text("""
            INSERT INTO dubicars (id, portal, brand, model, year, kilometrage, mileage, fuel, power, price, currency, country, location, url)
            VALUES (:id, :portal, :brand, :model, :year, :kilometrage, :mileage, :fuel, :power, :price, :currency, :country, :location, :url)
            ON CONFLICT (id) DO UPDATE SET
                price = EXCLUDED.price;
        """)
        
        params = {
            "id": test_id,
            "portal": "test",
            "brand": "TestBrand",
            "model": "TestModel",
            "year": 2024,
            "kilometrage": 0,
            "mileage": 0,
            "fuel": "Electric",
            "power": 100,
            "price": 1.0,
            "currency": "EUR",
            "country": "Spain",
            "location": "Madrid",
            "url": "https://example.com/test-car"
        }
        
        db.execute(query, params)
        db.commit()
        print("Commit SUCCESSFUL.")
        
        # Verify
        res = db.execute(text("SELECT * FROM dubicars WHERE id = :id"), {"id": test_id})
        row = res.fetchone()
        if row:
            print(f"Verification: Found record in DB! ID: {row[0]}")
        else:
            print("Verification FAILED: Record not found after commit.")
            
        db.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_insertion()
