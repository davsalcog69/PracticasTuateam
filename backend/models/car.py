from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, func, JSON
from sqlalchemy.orm import relationship
from core.database import Base

class Car(Base):
    __tablename__ = "cars"

    id = Column(String, primary_key=True, index=True)

    portal = Column(String)
    brand = Column(String)
    model = Column(String)
    version = Column(String)
    vehicle_status = Column(String, nullable=False, default="Dudoso")
    vehicle_status_check = Column(String, nullable=False, default="Dudoso")

    year = Column(Integer)
    kilometrage = Column(Integer)
    mileage = Column(Integer) # Alias for kilometrage

    fuel = Column(String)
    power = Column(Integer)

    price = Column(Float)
    currency = Column(String)

    country = Column(String)
    location = Column(String)

    url = Column(String)
    images = Column(JSON, default=[]) # Stored as ["url1", "url2"]

    inspections = relationship("InspectionRequest", back_populates="car")


class CarPriceHistory(Base):
    __tablename__ = "car_price_history"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String)
    model = Column(String)
    avg_price = Column(Float)
    currency = Column(String, default="EUR")
    sample_size = Column(Integer)
    source = Column(String, default="coches.net")
    created_at = Column(DateTime, server_default=func.now())