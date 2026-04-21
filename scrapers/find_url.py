import os
import sys
from sqlalchemy import text

# ROOT fix
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_ROOT = os.path.join(ROOT, "backend")
if ROOT not in sys.path: sys.path.insert(0, ROOT)
if BACKEND_ROOT not in sys.path: sys.path.insert(0, BACKEND_ROOT)

try:
    from backend.core.database import SessionLocal
    session = SessionLocal()
    
    # URL from the logs
    target_url = "https://www.dubicars.com/2022-mercedes-benz-e300-premium-20l-933410.html"
    
    for table in ['dubicars', 'cars']:
        query = text(f"SELECT count(*) FROM {table} WHERE id = :url OR url = :url")
        res = session.execute(query, {"url": target_url})
        count = res.scalar()
        print(f"URL found in '{table}': {count}")
        
    session.close()
except Exception as e:
    print(f"Error: {e}")
