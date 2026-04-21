import sys
import os
import argparse
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

# Add project root to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.database import SessionLocal
from repositories.scrape_run_repository import ScrapeRunRepository
from services.analysis_service import AnalysisService

# Import scrapers (assuming they are in the scrapers folder)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../scrapers")))
from portal_scrapers.coches_net import CochesNetScraper
# from portal_scrapers.emirates_auction import EmiratesAuctionScraper
from portal_scrapers.mobile_de import MobileDeScraper
from utils.db_repository import ScraperRepository

scheduler = BlockingScheduler()
run_repo = ScrapeRunRepository()
analysis_service = AnalysisService()

def run_scraper_job(portal_name: str, scraper_class, brand: str = "Mercedes", model: str = "Vito,Sprinter,Citan"):
    db = SessionLocal()
    run = run_repo.create_run(db, portal_name)
    print(f"[{datetime.now()}] Starting {portal_name} scraper...")
    
    try:
        scraper = scraper_class()
        ads = scraper.run(brand, model)
        
        # Save cars direct to DB as established in previous tasks
        scraper_repo = ScraperRepository()
        scraper_repo.save_cars(ads)
        
        # --- NEW PIPELINE STEP: DATABASE CLEANUP ---
        deleted_count = scraper_repo.cleanup_invalid_cars()
        
        run_repo.update_run(db, run.id, "COMPLETED", cars_scraped=len(ads))
        print(f"[{datetime.now()}] {portal_name} scraper finished.")
        print(f"[INFO] Scrapeados: {len(ads)}")
        print(f"[INFO] Guardados: {len(ads)}")
        print(f"[INFO] Eliminados de BD: {deleted_count}")
    except Exception as e:
        run_repo.update_run(db, run.id, "FAILED", errors=str(e))
        print(f"[{datetime.now()}] {portal_name} scraper failed: {e}")
    finally:
        db.close()

def run_analysis_job():
    db = SessionLocal()
    run = run_repo.create_run(db, "analysis_engine")
    print(f"[{datetime.now()}] Starting profitability analysis...")
    
    try:
        results = analysis_service.get_profitable_opportunities(db)
        run_repo.update_run(db, run.id, "COMPLETED", cars_scraped=len(results))
        print(f"[{datetime.now()}] Analysis finished. Opportunities detected: {len(results)}")
    except Exception as e:
        run_repo.update_run(db, run.id, "FAILED", errors=str(e))
        print(f"[{datetime.now()}] Analysis failed: {e}")
    finally:
        db.close()

# 1. Scraper coches.net every 12 hours
scheduler.add_job(run_scraper_job, 'interval', hours=12, args=["coches.net", CochesNetScraper], name="coches_net_12h")

# 2. Scraper mobile.de every 12 hours
scheduler.add_job(run_scraper_job, 'interval', hours=12, args=["mobile.de", MobileDeScraper], name="mobile_de_12h")

# 3. Scraper emiratesauction - REMOVED (Ignoring other portals)
# scheduler.add_job(run_scraper_job, 'interval', hours=24, args=["emiratesauction", EmiratesAuctionScraper], name="emirates_24h")

# 3. Analysis every 24 hours
scheduler.add_job(run_analysis_job, 'interval', hours=24, name="analysis_24h")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Car Import AI Automation Worker")
    parser.add_argument("--run", choices=["coches", "emirates", "analysis", "all"], help="Run a job manually once")
    args = parser.parse_args()

    if args.run == "coches":
        run_scraper_job("coches.net", CochesNetScraper)
    elif args.run == "emirates":
        run_scraper_job("emiratesauction", EmiratesAuctionScraper)
    elif args.run == "analysis":
        run_analysis_job()
    elif args.run == "all":
        run_scraper_job("coches.net", CochesNetScraper)
        run_scraper_job("emiratesauction", EmiratesAuctionScraper)
        run_analysis_job()
    else:
        print("Car Import AI - Automation Worker Started (Scheduler Mode)")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass

