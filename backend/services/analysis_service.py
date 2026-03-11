from sqlalchemy.orm import Session
from repositories.car_repository import CarRepository
from typing import List

class AnalysisService:
    def __init__(self):
        self.repository = CarRepository()

    def get_profitable_opportunities(self, db: Session) -> List[dict]:
        # 1. Get average prices in Spain (grouped by brand, model, year)
        spanish_prices = self.repository.get_spanish_avg_prices(db)
        
        # Create a lookup dictionary for easy comparison
        # Key: (brand, model, year) -> Value: avg_price
        avg_lookup = {
            (p.brand.lower(), p.model.lower(), p.year): p.avg_price 
            for p in spanish_prices
        }

        # 2. Get cars from Emirates
        emirates_cars = self.repository.get_emirates_cars(db)
        
        opportunities = []

        for car in emirates_cars:
            # Look for match in Spanish prices (±1 year)
            match_avg_price = None
            for year_offset in [-1, 0, 1]:
                key = (car.brand.lower(), car.model.lower(), car.year + year_offset)
                if key in avg_lookup:
                    match_avg_price = avg_lookup[key]
                    break
            
            if match_avg_price:
                # 3. Calculate costs
                # coste_total = p_emirates + 1500 (transp) + (p_emirates*0.1) + (p_emirates*0.21) + 1500 (homol) + 1000 (matric)
                p_emirates = car.price
                arancel = p_emirates * 0.10
                iva = p_emirates * 0.21
                coste_importacion = 1500 + arancel + iva + 1500 + 1000
                coste_total = p_emirates + coste_importacion
                
                # 4. Calculate margin
                margen = match_avg_price - coste_total
                
                # 5. Filter by profitability
                if margen > 3000:
                    opportunities.append({
                        "brand": car.brand,
                        "model": car.model,
                        "year_group": car.year,
                        "precio_medio_españa": round(match_avg_price, 2),
                        "precio_emirates": round(p_emirates, 2),
                        "coste_total_importación": round(coste_importacion, 2),
                        "margen_estimado": round(margen, 2),
                        "url_anuncio": car.url
                    })

        # 6. Sort by margin descending
        opportunities.sort(key=lambda x: x["margen_estimado"], reverse=True)
        
        return opportunities
