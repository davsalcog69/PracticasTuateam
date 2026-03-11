from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Car(Base):
    __tablename__ = "cars"

    id = Column(String, primary_key=True, index=True)
    brand = Column(String, index=True)
    model = Column(String, index=True)
    year = Column(Integer)
    mileage = Column(Integer)
    price = Column(Float)
    country = Column(String)
    url = Column(String)
    
    images = relationship("CarImage", back_populates="car")
    inspections = relationship("InspectionRequest", back_populates="car")

class CarImage(Base):
    __tablename__ = "car_images"

    id = Column(String, primary_key=True, index=True)
    car_id = Column(String, ForeignKey("cars.id"))
    image_url = Column(String)

    car = relationship("Car", back_populates="images")
