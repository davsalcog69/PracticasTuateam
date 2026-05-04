import os
import sys
from sqlalchemy import text

# --- PATH FIX ---
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_ROOT = os.path.join(ROOT, "backend")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

try:
    from backend.core.database import SessionLocal
    HAS_DB = True
except ImportError:
    HAS_DB = False
    print("[ERROR] No se pudo encontrar SessionLocal para limpiar la base de datos.")

def clear_test_data():
    if not HAS_DB:
        return

    session = SessionLocal()
    try:
        print("[INFO] Limpiando datos de prueba...")
        
        # Borramos las exportaciones primero
        try:
            print("[INFO] Limpiando tabla 'car_export'...")
            session.execute(text("DELETE FROM car_export"))
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"[WARNING] No se pudo limpiar 'car_export': {e}")
        
        # Luego borramos los coches
        try:
            print("[INFO] Limpiando tabla 'cars'...")
            result = session.execute(text("DELETE FROM cars"))
            session.commit()
            print(f"[OK] Se ha limpiado la base de datos correctamente ({result.rowcount} coches base eliminados).")
        except Exception as e:
            session.rollback()
            print(f"[ERROR] Error al limpiar 'cars': {e}")
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Error al limpiar los datos: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    clear_test_data()
