import uuid
from datetime import datetime
from core.database import SessionLocal
from models.car import Car, CarImage
from models.car_export import CarExport

def insert_mock_data():
    db = SessionLocal()
    try:
        # 1. Clean existing mock data (optional but good for consistency)
        db.query(CarExport).filter(CarExport.portal == "mobile.de").delete()
        db.query(CarImage).filter(CarImage.car_id.like("mock-%")).delete()
        db.query(Car).filter(Car.portal == "mobile.de").delete()
        db.commit()

        mercedes_models = [
            ("Mercedes-Benz", "Vito", 28500, 2023, 12000, 163, "Berlin, Germany"),
            ("Mercedes-Benz", "Vito", 32000, 2024, 5000, 190, "Munich, Germany"),
            ("Mercedes-Benz", "Sprinter", 42000, 2023, 25000, 170, "Hamburg, Germany"),
            ("Mercedes-Benz", "Sprinter", 39500, 2023, 45000, 150, "Frankfurt, Germany"),
            ("Mercedes-Benz", "Citan", 21000, 2023, 8000, 116, "Cologne, Germany"),
            ("Mercedes-Benz", "Citan", 23500, 2024, 2000, 116, "Stuttgart, Germany"),
            ("Mercedes-Benz", "Vito", 29900, 2023, 15000, 163, "Düsseldorf, Germany"),
            ("Mercedes-Benz", "Vito", 31500, 2023, 10000, 163, "Leipzig, Germany"),
            ("Mercedes-Benz", "Sprinter", 45000, 2024, 1000, 190, "Dortmund, Germany"),
            ("Mercedes-Benz", "Sprinter", 38000, 2023, 30000, 150, "Essen, Germany"),
            ("Mercedes-Benz", "Citan", 22500, 2023, 12000, 110, "Bremen, Germany"),
            ("Mercedes-Benz", "Vito", 27000, 2023, 22000, 136, "Dresden, Germany"),
            ("Mercedes-Benz", "Vito", 34000, 2024, 4000, 190, "Hanover, Germany"),
            ("Mercedes-Benz", "Sprinter", 41000, 2023, 18000, 170, "Nuremberg, Germany"),
            ("Mercedes-Benz", "Citan", 24000, 2024, 500, 116, "Duisburg, Germany"),
        ]

        images = [
            "https://images.unsplash.com/photo-1542362567-b05500269774?auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1580273916550-e323be2ae537?auto=format&fit=crop&q=80"
        ]

        for i, (brand, model, price, year, mileage, power, location) in enumerate(mercedes_models):
            car_id = f"mock-{uuid.uuid4().hex[:8]}"
            
            # Create Raw Car
            car = Car(
                id=car_id,
                portal="mobile.de",
                brand=brand,
                model=model,
                version="Extra Long BlueTEC",
                year=year,
                kilometrage=mileage,
                fuel="Diésel",
                power=power,
                price=float(price),
                currency="EUR",
                country="Germany",
                location=location,
                url=f"https://suchen.mobile.de/fahrzeuge/details.html?id={i}"
            )
            db.add(car)

            # Add Image
            car_image = CarImage(
                id=f"img-{car_id}",
                car_id=car_id,
                image_url=images[i % len(images)]
            )
            db.add(car_image)

            # Create Export Record
            import_tax = 0  # EU Import
            transport_cost = 1500
            registration_cost = 600
            gestor_cost = 400
            total_import_cost = price + transport_cost + registration_cost + gestor_cost
            
            # Mock estimation based on current price + 25% for Spain market
            price_spain_avg = total_import_cost * 1.25 
            estimated_profit = price_spain_avg - total_import_cost

            exported_car = CarExport(
                id=car_id,
                portal="mobile.de",
                brand=brand,
                model=model,
                fuel="Diésel",
                year=year,
                mileage=mileage,
                power=power,
                price=float(price),
                currency="EUR",
                price_eur=float(price),
                price_spain_avg=float(price_spain_avg),
                country="Germany",
                location=location,
                url=car.url,
                transport_cost=float(transport_cost),
                import_tax=float(import_tax),
                itv_cost=0.0,
                registration_cost=float(registration_cost),
                gestor_cost=float(gestor_cost),
                total_import_cost=float(total_import_cost),
                final_price=float(total_import_cost),
                estimated_profit=float(estimated_profit),
                created_at=datetime.now()
            )
            db.add(exported_car)

        db.commit()
        print(f"Successfully inserted {len(mercedes_models)} mock Mercedes records for Mobile.de")

    except Exception as e:
        db.rollback()
        print(f"Error inserting mock data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    insert_mock_data()
