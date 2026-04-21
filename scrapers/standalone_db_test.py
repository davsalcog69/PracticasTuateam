import os
import sys
from sqlalchemy import text

# ROOT fix
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_ROOT = os.path.join(ROOT, "backend")
if ROOT not in sys.path: sys.path.insert(0, ROOT)
if BACKEND_ROOT not in sys.path: sys.path.insert(0, BACKEND_ROOT)

def run_direct_test():
    try:
        from backend.core.database import SessionLocal
        from backend.core.config import settings
        
        print(f"URL: {settings.DATABASE_URL.split('@')[-1]}")
        session = SessionLocal()
        
        test_url = "https://test.com/v1"
        print(f"Inserting {test_url}...")
        
        query = text("""
            INSERT INTO dubicars (id, portal, brand, model, year, price, url)
            VALUES (:id, :portal, :brand, :model, :year, :price, :url)
            ON CONFLICT (id) DO UPDATE SET price = EXCLUDED.price;
        """)
        
        params = {
            "id": test_url,
            "portal": "test",
            "brand": "Test",
            "model": "Test",
            "year": 2024,
            "price": 99.9,
            "url": test_url
        }
        
        session.execute(query, params)
        print("Execute finished. Committing...")
        session.commit()
        print("Commit finished.")
        
        # Verify immediately
        res = session.execute(text("SELECT count(*) FROM dubicars WHERE id = :id"), {"id": test_url})
        count = res.scalar()
        print(f"Verification count: {count}")
        
        session.close()
        print("Test Complete.")
        
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_direct_test()
