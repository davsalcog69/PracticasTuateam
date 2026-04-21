from sqlalchemy.orm import Session
from models.car import Car, CarPriceHistory

class CarRepository:
    def get_all_cars(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Car)\
            .filter(Car.portal == "mobile.de", Car.year >= 2023, Car.year <= 2026)\
            .offset(skip).limit(limit).all()

    def get_cars_by_model(self, db: Session, brand: str, model: str):
        return db.query(Car)\
            .filter(
                Car.brand.ilike(f"%{brand}%"), 
                Car.model.ilike(f"%{model}%"),
                Car.portal == "mobile.de",
                Car.year >= 2023,
                Car.year <= 2026
            ).all()

    def count_cars_by_model(self, db: Session, brand: str, model: str):
        return db.query(Car).filter(
            Car.brand.ilike(f"%{brand}%"), 
            Car.model.ilike(f"%{model}%"),
            Car.portal == "mobile.de",
            Car.year >= 2023,
            Car.year <= 2026
        ).count()

    def get_spanish_avg_prices(self, db: Session):
        from sqlalchemy import func
        return db.query(
            Car.brand,
            Car.model,
            Car.year,
            func.avg(Car.price).label("avg_price"),
            func.count(Car.id).label("sample_size")
        ).filter(Car.portal == "coches.net").group_by(
            Car.brand, Car.model, Car.year
        ).all()

    def save_price_history(self, db: Session, brand: str, model: str, avg_price: float, sample_size: int, currency: str = "EUR", source: str = "coches.net"):
        history_entry = CarPriceHistory(
            brand=brand,
            model=model,
            avg_price=avg_price,
            sample_size=sample_size,
            currency=currency,
            source=source
        )
        db.add(history_entry)
        db.commit()
        db.refresh(history_entry)
        return history_entry

    def get_mobile_de_cars(self, db: Session):
        return db.query(Car)\
            .filter(Car.portal == "mobile.de", Car.year >= 2023, Car.year <= 2026).all()

    def get_exported_cars(self, db: Session, skip: int = 0, limit: int = 100):
        from models.car_export import CarExport
        return db.query(CarExport)\
            .filter(CarExport.year >= 2023, CarExport.year <= 2026)\
            .offset(skip).limit(limit).all()

    def count_exported_cars(self, db: Session):
        from models.car_export import CarExport
        return db.query(CarExport).filter(CarExport.year >= 2023, CarExport.year <= 2026).count()
