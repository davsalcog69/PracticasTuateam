import sys
import os
import logging
from sqlalchemy import create_engine, text

# Setup paths
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_ROOT = os.path.join(ROOT, "backend")
if ROOT not in sys.path: sys.path.insert(0, ROOT)
if BACKEND_ROOT not in sys.path: sys.path.insert(0, BACKEND_ROOT)

from backend.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Migration")

def migrate():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        try:
            # Check if roi_percentage exists
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='car_export' AND column_name='roi_percentage'"))
            if not res.fetchone():
                logger.info("Adding roi_percentage to car_export...")
                conn.execute(text("ALTER TABLE car_export ADD COLUMN roi_percentage DOUBLE PRECISION"))
                conn.execute(text("UPDATE car_export SET roi_percentage = 0.0 WHERE roi_percentage IS NULL"))
                conn.commit()
                logger.info("Migration successful.")
            else:
                logger.info("roi_percentage already exists.")
        except Exception as e:
            # SQLite fallback syntax
            if "information_schema" in str(e):
                try:
                    conn.execute(text("ALTER TABLE car_export ADD COLUMN roi_percentage REAL DEFAULT 0.0"))
                    conn.commit()
                    logger.info("SQLite migration successful.")
                except Exception as e2:
                    if "duplicate column name" in str(e2):
                         logger.info("roi_percentage already exists in SQLite.")
                    else:
                         logger.error(f"SQLite migration error: {e2}")
            else:
                logger.error(f"Migration error: {e}")

if __name__ == "__main__":
    migrate()
