from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class CarAdSchema(BaseModel):
    portal: str
    brand: str
    model: str
    year: int
    mileage: Optional[int] = None
    fuel: str
    power: Optional[int] = None
    price: float
    currency: str = "EUR"
    country: str = "España"
    location: Optional[str] = None
    url: HttpUrl
    source_url: Optional[str] = None
    images: List[HttpUrl] = []
    scraped_at: datetime = datetime.now()

    class Config:
        json_schema_extra = {
            "example": {
                "brand": "OPEL",
                "model": "Crossland X",
                "year": 2019,
                "mileage": 76000,
                "fuel": "Gasolina",
                "power": 110,
                "price": 13900.0,
                "currency": "EUR",
                "country": "España",
                "url": "https://www.coches.net/ad/123",
                "images": ["https://example.com/img1.jpg"]
            }
        }
