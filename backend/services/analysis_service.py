from sqlalchemy.orm import Session
from repositories.car_repository import CarRepository
from typing import List

class AnalysisService:
    def __init__(self):
        self.repository = CarRepository()

    def get_profitable_opportunities(self, db: Session) -> List[dict]:
        # 1. Get average prices in Spain (grouped by brand, model, year)
        spanish_prices = self.repository.get_spanish_avg_prices(db)
        
        # Save historical data
        for p in spanish_prices:
            if p.avg_price > 0 and p.sample_size >= 3:
                self.repository.save_price_history(
                    db, 
                    brand=p.brand, 
                    model=p.model, 
                    avg_price=p.avg_price, 
                    sample_size=p.sample_size
                )

        # Create a lookup dictionary for easy comparison
        avg_lookup = {
            (p.brand.lower(), p.model.lower(), p.year): p.avg_price 
            for p in spanish_prices
        }

        # 2. Get cars from Mobile.de
        mobile_cars = self.repository.get_mobile_de_cars(db)
        
        opportunities = []

        for car in mobile_cars:
            # Look for match in Spanish prices (±1 year for better sample)
            match_avg_price = None
            for year_offset in [-1, 0, 1]:
                key = (car.brand.lower(), car.model.lower(), car.year + year_offset)
                if key in avg_lookup:
                    match_avg_price = avg_lookup[key]
                    break
            
            if match_avg_price:
                # 3. Calculate costs (Simplified EU Import: Germany -> Spain)
                # No Arancel (EU), No specific VAT adjustment if already included
                # Estimated: 1500 (Transport) + 1000 (Matriculation/ITV) = 2500
                p_mobile = car.price
                coste_importacion = 2500 
                coste_total = p_mobile + coste_importacion
                
                # 4. Calculate margin
                margen = match_avg_price - coste_total
                
                # 5. Filter by profitability
                if margen > 2000: # Slightly lower threshold for EU opportunities
                    opportunities.append({
                        "brand": car.brand,
                        "model": car.model,
                        "year_group": car.year,
                        "precio_medio_españa": round(match_avg_price, 2),
                        "precio_mobile": round(p_mobile, 2),
                        "coste_total_importación": round(coste_importacion, 2),
                        "margen_estimado": round(margen, 2),
                        "url_anuncio": car.url
                    })

        # 6. Sort by margin descending
        opportunities.sort(key=lambda x: x["margen_estimado"], reverse=True)
        
        return opportunities
