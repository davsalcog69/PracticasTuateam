from sqlalchemy.orm import Session
from repositories.car_repository import CarRepository

class CarService:
    def __init__(self):
        self.repository = CarRepository()

    def get_all_cars(self, db: Session, skip: int = 0, limit: int = 100):
        return self.repository.get_all_cars(db, skip, limit)

    def get_cars_by_model(self, db: Session, brand: str, model: str):
        cars = self.repository.get_cars_by_model(db, brand, model)
        total = self.repository.count_cars_by_model(db, brand, model)
        return {
            "brand": brand,
            "model": model,
            "total_results": total,
            "cars": cars
        }
