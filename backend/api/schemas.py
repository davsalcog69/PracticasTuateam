from pydantic import BaseModel, field_validator
from typing import List, Optional, Any
from datetime import datetime


class CarSchema(BaseModel):
    id: str
    portal: str
    brand: str
    model: str
    version: Optional[str] = None
    vehicle_status: str = "Dudoso"
    vehicle_status_check: str = "Dudoso"
    year: int
    kilometrage: int
    fuel: str
    power: Optional[int] = None
    price: float
    currency: str = "EUR"
    country: str
    location: str
    url: str
    images: List[str] = []

    class Config:
        from_attributes = True

class ModelResponse(BaseModel):
    brand: str
    model: str
    total_results: int
    cars: List[CarSchema]

class InspectionCreate(BaseModel):
    car_id: str
    name: str
    email: str
    phone: str
    message: Optional[str] = None

class InspectionResponse(BaseModel):
    id: str
    car_id: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProfitableCarResponse(BaseModel):
    brand: str
    model: str
    year_group: int
    precio_medio_españa: float
    precio_emirates: float
    coste_total_importación: float
    margen_estimado: float
    url_anuncio: str

class CarExportSchema(BaseModel):
    id: str
    portal: str
    brand: str
    model: str
    vehicle_status: str = "Dudoso"
    vehicle_status_check: str = "Dudoso"
    year: int
    mileage: int
    fuel: str
    power: Optional[int] = None
    
    price: float
    currency: str
    price_eur: float
    price_spain_avg: float
    
    country: str
    location: str
    url: str
    
    transport_cost: Optional[float] = 0.0
    import_tax: Optional[float] = 0.0
    itv_cost: Optional[float] = 0.0
    registration_cost: Optional[float] = 0.0
    gestor_cost: Optional[float] = 0.0
    total_import_cost: Optional[float] = 0.0
    final_price: Optional[float] = 0.0
    estimated_profit: Optional[float] = 0.0
    roi_percentage: Optional[float] = 0.0
    
    created_at: Optional[datetime] = None
    images: List[str] = []

    @field_validator('images', mode='before')
    @classmethod
    def ensure_list(cls, v: Any) -> List[str]:
        if isinstance(v, list):
            return v
        if not v or isinstance(v, dict):
            return []
        import json
        if isinstance(v, str):
            try: return json.loads(v)
            except: return []
        return []

    class Config:
        from_attributes = True

class ExportedCarResponse(BaseModel):
    total: int
    cars: List[CarExportSchema]

class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    car_id: str
    car: Optional[CarExportSchema] = None
    created_at: datetime

    class Config:
        from_attributes = True

