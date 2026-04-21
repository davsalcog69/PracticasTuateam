import os
import sys
import logging
from sqlalchemy import text

# --- PATH FIX TO FIND BACKEND ---
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_ROOT = os.path.join(ROOT, "backend")
if ROOT not in sys.path: sys.path.insert(0, ROOT)
if BACKEND_ROOT not in sys.path: sys.path.insert(0, BACKEND_ROOT)

from backend.core.database import SessionLocal
from portal_scrapers.mobile_de import FALLBACK_IMAGE

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("Cleanup")

def cleanup():
    session = SessionLocal()
    try:
        logger.info("Iniciando purga de registros incompletos...")
        
        # 1. Eliminar registros con kilometraje 0 o nulo
        query_mileage = text("DELETE FROM cars WHERE mileage = 0 OR kilometrage = 0 OR mileage IS NULL")
        res_mileage = session.execute(query_mileage)
        logger.info(f"Purga Kilometraje (cars): Eliminados {res_mileage.rowcount} registros con 'mileage = 0'.")
        
        # 1b. También en car_export (frontend)
        query_mileage_export = text("DELETE FROM car_export WHERE mileage = 0 OR mileage IS NULL")
        res_mileage_export = session.execute(query_mileage_export)
        logger.info(f"Purga Kilometraje (car_export): Eliminados {res_mileage_export.rowcount} registros con 'mileage = 0'.")
        
        # 2. Eliminar registros que usan la imagen de fallback o no tienen imágenes
        query_images = text(f"DELETE FROM cars WHERE images::text LIKE :fallback OR images::text = '[]' OR images IS NULL")
        res_images = session.execute(query_images, {"fallback": f"%{FALLBACK_IMAGE}%"})
        logger.info(f"Purga Imágenes (cars): Eliminados {res_images.rowcount} registros con fallback o sin fotos.")
        
        # 2b. También en car_export (frontend)
        query_images_export = text(f"DELETE FROM car_export WHERE images::text LIKE :fallback OR images::text = '[]' OR images IS NULL")
        res_images_export = session.execute(query_images_export, {"fallback": f"%{FALLBACK_IMAGE}%"})
        logger.info(f"Purga Imágenes (car_export): Eliminados {res_images_export.rowcount} registros con fallback o sin fotos.")
        
        # 3. Eliminar huérfanos en car_export (registros que ya no están en 'cars')
        query_orphans = text("DELETE FROM car_export WHERE id NOT IN (SELECT id FROM cars)")
        res_orphans = session.execute(query_orphans)
        logger.info(f"Purga Huérfanos (car_export): Eliminados {res_orphans.rowcount} registros sin correspondencia en 'cars'.")
        
        # 4. Control Estricto de Rentabilidad
        query_profit = text("DELETE FROM car_export WHERE estimated_profit < 500 OR estimated_profit IS NULL")
        res_profit = session.execute(query_profit)
        logger.info(f"Purga Rentabilidad (car_export): Eliminados {res_profit.rowcount} registros con rentabilidad menor a 500€.")
        
        session.commit()
        logger.info("Limpieza automática completada exitosamente.")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error durante la limpieza: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    cleanup()
