import os
import sys
import json
from sqlalchemy import text, inspect

# --- PATH FIX ---
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_ROOT = os.path.join(ROOT, "backend")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

try:
    from backend.core.database import SessionLocal, engine
    HAS_DB = True
except ImportError:
    HAS_DB = False

def run_migration():
    if not HAS_DB:
        print("[ERROR] No se pudo conectar a la base de datos.")
        return

    session = SessionLocal()
    conn = session.connection()
    try:
        # 1. DROP OBSOLETE TABLE
        print("[INFO] Borrando tabla obsoleta 'cars_mobile'...")
        session.execute(text("DROP TABLE IF EXISTS cars_mobile CASCADE"))

        # 2. ADD IMAGES COLUMN (Safe addition)
        inspector = inspect(engine)
        
        # Para la tabla 'cars'
        columns_cars = [c['name'] for c in inspector.get_columns("cars")]
        if "images" not in columns_cars:
            print("[INFO] Añadiendo columna 'images' a tabla 'cars'...")
            session.execute(text("ALTER TABLE cars ADD COLUMN images JSONB DEFAULT '[]'::jsonb"))
            # También añadimos 'mileage' como alias si no existe
            if "mileage" not in columns_cars:
                session.execute(text("ALTER TABLE cars ADD COLUMN mileage INTEGER"))
        
        # Para la tabla 'car_export'
        columns_export = [c['name'] for c in inspector.get_columns("car_export")]
        if "images" not in columns_export:
            print("[INFO] Añadiendo columna 'images' a tabla 'car_export'...")
            session.execute(text("ALTER TABLE car_export ADD COLUMN images JSONB DEFAULT '[]'::jsonb"))

        # 3. MIGRATE DATA FROM car_images (Optional but good practice)
        if "car_images" in inspector.get_table_names():
            print("[INFO] Migrando datos de 'car_images' a 'cars.images'...")
            # Esta es una query de migración de Postgres
            migration_query = """
                UPDATE cars c
                SET images = (
                    SELECT json_agg(image_url)
                    FROM car_images ci
                    WHERE ci.car_id = c.id
                )
                WHERE EXISTS (SELECT 1 FROM car_images ci WHERE ci.car_id = c.id);
            """
            session.execute(text(migration_query))
            
            # Idem para car_export si tiene algo
            migration_export_query = """
                UPDATE car_export ce
                SET images = (
                    SELECT json_agg(image_url)
                    FROM car_images ci
                    WHERE ci.car_id = ce.id
                )
                WHERE EXISTS (SELECT 1 FROM car_images ci WHERE ci.car_id = ce.id);
            """
            session.execute(text(migration_export_query))
            
            # 4. DROP car_images
            print("[INFO] Borrando tabla 'car_images'...")
            session.execute(text("DROP TABLE car_images CASCADE"))

        session.commit()
        print("[OK] Migración completada con éxito.")
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Error durante la migración: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    run_migration()
