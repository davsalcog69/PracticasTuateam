from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class CarAdSchema(BaseModel):
    portal: str
    brand: str
    model: str
    version: Optional[str] = None
    year: int
    kilometrage: int
    fuel: str
    power: Optional[int] = None
    price: float
    currency: str = "EUR"
    location: str
    url: HttpUrl
    images: List[HttpUrl] = []
    scraped_at: datetime = datetime.now()

    class Config:
        schema_extra = {
            "example": {
                "brand": "BMW",
                "model": "Serie 3",
                "version": "320d",
                "year": 2021,
                "kilometrage": 45000,
                "fuel": "Diesel",
                "power": 190,
                "price": 24500.0,
                "currency": "EUR",
                "location": "Múnich, Alemania",
                "url": "https://example.com/ad/123",
                "images": ["https://example.com/img1.jpg"]
            }
        }
