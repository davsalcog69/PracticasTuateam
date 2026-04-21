import os
import sys

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

try:
    from main import app
    from core.database import SessionLocal
    from services.car_service import CarService
    
    db = SessionLocal()
    service = CarService()
    cars = service.get_all_cars(db)
    print(f"Success: Found {len(cars)} cars")
    db.close()
except Exception as e:
    import traceback
    print("Caught Exception:")
    traceback.print_exc()
    sys.exit(1)
