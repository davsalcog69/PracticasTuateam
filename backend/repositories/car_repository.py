from sqlalchemy.orm import Session
from models.car import Car

class CarRepository:
    def get_all_cars(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Car).offset(skip).limit(limit).all()

    def get_cars_by_model(self, db: Session, brand: str, model: str):
        return db.query(Car).filter(
            Car.brand.ilike(f"%{brand}%"), 
            Car.model.ilike(f"%{model}%")
        ).all()

    def count_cars_by_model(self, db: Session, brand: str, model: str):
        return db.query(Car).filter(
            Car.brand.ilike(f"%{brand}%"), 
            Car.model.ilike(f"%{model}%")
        ).count()

    def get_spanish_avg_prices(self, db: Session):
        from sqlalchemy import func
        return db.query(
            Car.brand,
            Car.model,
            Car.year,
            func.avg(Car.price).label("avg_price")
        ).filter(Car.portal == "coches.net").group_by(
            Car.brand, Car.model, Car.year
        ).all()

    def get_emirates_cars(self, db: Session):
        return db.query(Car).filter(Car.portal == "emiratesauction").all()

