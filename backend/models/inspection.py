from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

class InspectionRequest(Base):
    __tablename__ = "inspection_requests"

    id = Column(String, primary_key=True, index=True)
    car_id = Column(String, ForeignKey("cars.id"))
    user_name = Column(String)
    user_email = Column(String)
    user_phone = Column(String)
    notes = Column(String)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    car = relationship("Car", back_populates="inspections")
