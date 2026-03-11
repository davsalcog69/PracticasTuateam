from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CarImageSchema(BaseModel):
    id: str
    image_url: str

    class Config:
        orm_mode = True

class CarSchema(BaseModel):
    id: str
    brand: str
    model: str
    year: int
    mileage: int
    price: float
    country: str
    url: str
    images: List[CarImageSchema] = []

    class Config:
        orm_mode = True

class ModelResponse(BaseModel):
    brand: str
    model: str
    total_results: int
    cars: List[CarSchema]

class InspectionCreate(BaseModel):
    car_id: str
    user_name: str
    user_email: str
    user_phone: str
    notes: Optional[str] = None

class InspectionResponse(BaseModel):
    id: str
    car_id: str
    status: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class ProfitableCarResponse(BaseModel):
    brand: str
    model: str
    year_group: int
    precio_medio_españa: float
    precio_emirates: float
    coste_total_importación: float
    margen_estimado: float
    url_anuncio: str

