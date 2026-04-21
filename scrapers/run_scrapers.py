from portal_scrapers.coches_net import CochesNetScraper
from portal_scrapers.mobile_de import MobileDeScraper
from utils.db_repository import ScraperRepository
import argparse
import sys

class TargetedPipeline:
    def __init__(self, target_count=20):
        self.repo = ScraperRepository()
        self.target_count = target_count
        self.counts = {"Vito": 0, "Sprinter": 0, "Citan": 0}
        self.total_scraped = 0
        self.total_saved = 0
        self.current_portal = "unknown"

    def reset_counts(self):
        self.counts = {"Vito": 0, "Sprinter": 0, "Citan": 0}

    def is_finished(self):
        return all(count >= self.target_count for count in self.counts.values())

    def process_item(self, item, table_name="cars"):
        self.total_scraped += 1
        model = item.model
        
        # Validation: URL
        url_str = str(item.url) if item.url else ""
        if not url_str or not url_str.startswith("http"):
             return False
        
        if model not in self.counts:
            # print(f"[SKIP] {item.brand} {model}")
            return False

        if self.counts[model] >= self.target_count:
            return False

        # Save to DB
        try:
            # Ensure portal is set correctly for logging/storage
            item.portal = self.current_portal
            
            self.repo.save_cars([item], table_name=table_name)
            self.counts[model] += 1
            self.total_saved += 1
            print(f"[OK] {self.current_portal} {model} guardado en '{table_name}' ({self.counts[model]}/{self.target_count})")
            return True
        except Exception as e:
            print(f"[ERROR] Fail saving {model} to {table_name}: {e}")
            return False

    def report(self, portal_label):
        print(f"\n========================================")
        print(f"REPORT FOR {portal_label}")
        for model, count in self.counts.items():
            print(f"{model}: {count}")
        print(f"========================================\n")

async def run_targeted_scraping():
    pipeline = TargetedPipeline(target_count=20)
    
    # 1. Coches.net (Internal baseline for price comparison)
    print(f"\n[INFO] Ejecutando scraper coches.net (Baseline de precios España)")
    pipeline.current_portal = "coches.net"
    coches_scraper = CochesNetScraper()
    try:
        # We still scrape to have average prices for ROI calculation
        await coches_scraper.scrape_for_pipeline(pipeline)
    except Exception as e:
        print(f"[CRITICAL] Coches.net failed: {e}")

    pipeline.report("Coches.net")
    pipeline.reset_counts() 

    # 2. Mobile.de (Primary Marketplace Source)
    print(f"\n[INFO] Ejecutando scraper mobile.de (Fuente principal)")
    pipeline.current_portal = "mobile.de"
    mobile_scraper = MobileDeScraper()
    try:
        # Saving to main 'cars' table for frontend visibility
        await mobile_scraper.scrape_for_pipeline(pipeline)
    except Exception as e:
        print(f"[CRITICAL] Mobile.de failed: {e}")
    
    pipeline.report("Mobile.de")

    # 3. ROI Calculation & Export to Dashboard (car_export)
    print(f"\n[INFO] Ejecutando análisis de ROI y Exportación a Dashboard...")
    from utils.comparison_engine import ComparisonEngine
    import os
    from backend.core.config import settings
    
    db_url = os.getenv("DATABASE_URL") or settings.DATABASE_URL
    engine = ComparisonEngine(db_url)
    try:
        await engine.run_export_process()
        print(f"[OK] Análisis completado. Coches rentables exportados a 'car_export'.")
    except Exception as e:
        print(f"[ERROR] Error en el análisis de ROI: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_targeted_scraping())
