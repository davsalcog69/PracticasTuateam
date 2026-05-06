import sys
import os
import math
import argparse
import traceback
from time import time
from multiprocessing import Pool, cpu_count
from portal_scrapers.coches_net import CochesNetScraper
from utils.db_repository import ScraperRepository
from base.schemas import CarAdSchema

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

def worker_task(worker_config):
    """
    Independent worker task that runs its own browser instance.
    Requirement 1 & 2: Multi-worker and Browser reuse.
    """
    worker_id = worker_config['id']
    start_page = worker_config['start_page']
    end_page = worker_config['end_page']
    brand = worker_config['brand']
    model = worker_config['model']

    print(f"[*] Worker-{worker_id} starting: Pages {start_page} to {end_page}")
    
    scraper = CochesNetScraper()
    scraper.worker_id = f"Worker-{worker_id}"
    repo = ScraperRepository()
    
    total_extracted = 0
    try:
        # Scrape the assigned range (Requirement 3)
        # Using the new anti-blocking network layer (requests based)
        raw_ads = scraper.scrape_list(None, brand, model, start_page, end_page)
        
        if raw_ads:
            # Validate results using the existing schema
            validated_ads = []
            for raw_ad in raw_ads:
                try:
                    # Portal is already in raw_ad from scraper.scrape_list
                    validated_ads.append(CarAdSchema(**raw_ad))
                except Exception as e:
                    print(f"[!] Worker-{worker_id} validation error: {e}")
            
            # Safe result handling: Batch insert into database (Requirement 9)
            if validated_ads:
                repo.save_cars(validated_ads)
                total_extracted = len(validated_ads)
        
        print(f"[+] Worker-{worker_id} finished: {total_extracted} cars saved.")
        return total_extracted
        
    except Exception as e:
        print(f"[!] Worker-{worker_id} CRITICAL ERROR: {e}")
        traceback.print_exc()
        return 0
    finally:
        # No browser to stop in the new implementation
        pass

def main():
    parser = argparse.ArgumentParser(description="HIGH PERFORMANCE Coches.net Parallel Scraper")
    parser.add_argument("--total-pages", type=int, default=100, help="Total number of pages to scrape")
    parser.add_argument("--workers", type=int, default=3, help="Number of parallel workers (Recommended: 3-5)")
    parser.add_argument("--brand", type=str, default="", help="Filter by brand")
    parser.add_argument("--model", type=str, default="", help="Filter by model")
    
    args = parser.parse_args()
    
    # Worker Orchestrator Logic (Requirement 4)
    total_pages = args.total_pages
    num_workers = min(args.workers, total_pages)
    pages_per_worker = math.ceil(total_pages / num_workers)
    
    print("\n" + "="*50)
    print(f"      COCHES.NET PARALLEL SCRAPER ORCHESTRATOR")
    print("="*50)
    print(f"[*] Total Pages: {total_pages}")
    print(f"[*] Total Workers: {num_workers}")
    print(f"[*] Pages per worker: {pages_per_worker}")
    print("="*50 + "\n")
    
    start_time = time()
    
    # Prepare worker configurations
    worker_configs = []
    for i in range(num_workers):
        start_p = (i * pages_per_worker) + 1
        end_p = min((i + 1) * pages_per_worker, total_pages)
        if start_p > total_pages:
            break
        worker_configs.append({
            'id': i + 1,
            'start_page': start_p,
            'end_page': end_p,
            'brand': args.brand,
            'model': args.model
        })

    # Launch workers using a Pool (Requirement 1)
    with Pool(processes=num_workers) as pool:
        results = pool.map(worker_task, worker_configs)
    
    end_time = time()
    duration = end_time - start_time
    total_cars = sum(results)
    
    print("\n" + "="*50)
    print(f"SCRAPING COMPLETE")
    print("="*50)
    print(f"[*] Time taken: {duration:.2f} seconds")
    print(f"[*] Total cars extracted: {total_cars}")
    print(f"[*] Performance: {total_cars / (duration/60):.2f} cars/minute")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
