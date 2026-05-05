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
logger = logging.getLogger("RecalculateROI")

def recalculate():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        try:
            # Recalculate roi_percentage based on existing estimated_profit and final_price
            query = text("""
                UPDATE car_export 
                SET roi_percentage = ROUND(CAST((estimated_profit / final_price) * 100.0 AS numeric), 2)
                WHERE final_price > 0 AND (roi_percentage IS NULL OR roi_percentage = 0.0)
            """)
            result = conn.execute(query)
            conn.commit()
            logger.info(f"Successfully recalculated ROI for {result.rowcount} vehicles.")
        except Exception as e:
            logger.error(f"Error recalculating ROI: {e}")

if __name__ == "__main__":
    recalculate()
