import asyncio
import os
import sys

# --- PATH FIX ---
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.comparison_engine import ComparisonEngine
from backend.core.config import settings

async def test_roi():
    db_url = os.getenv("DATABASE_URL") or settings.DATABASE_URL
    print(f"[INFO] Iniciando análisis de ROI... DB: {db_url[:20]}...")
    engine = ComparisonEngine(db_url)
    try:
        await engine.run_export_process()
        print(f"[OK] Análisis completado con éxito.")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_roi())
