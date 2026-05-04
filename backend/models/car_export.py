from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from core.database import Base

class CarExport(Base):
    __tablename__ = "car_export"

    id = Column(String, primary_key=True, index=True)
    portal = Column(String)
    brand = Column(String)
    model = Column(String)
    vehicle_status = Column(String, nullable=False, default="Dudoso")
    vehicle_status_check = Column(String, nullable=False, default="Dudoso")
    fuel = Column(String)
    year = Column(Integer)
    mileage = Column(Integer)
    power = Column(Integer)
    
    price = Column(Float)
    currency = Column(String)
    price_eur = Column(Float)
    price_spain_avg = Column(Float)
    
    country = Column(String)
    location = Column(String)
    url = Column(String)
    images = Column(JSON, default=[]) # Stored as ["url1", "url2"]
    
    transport_cost = Column(Float)
    import_tax = Column(Float)
    itv_cost = Column(Float)
    registration_cost = Column(Float)
    gestor_cost = Column(Float)
    total_import_cost = Column(Float)
    final_price = Column(Float)
    estimated_profit = Column(Float)
    
    created_at = Column(DateTime)
