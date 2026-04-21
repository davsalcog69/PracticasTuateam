import asyncio
import logging
import sys
import os

# --- PATH FIX ---
sys.path.insert(0, os.getcwd())

from portal_scrapers.mobile_de import MobileDeScraper

logging.basicConfig(level=logging.INFO)

async def test():
    scraper = MobileDeScraper(worker_id="TestValidator")
    
    class MockPipeline:
        def __init__(self):
            self.counts = {"Vito": 0, "Sprinter": 0, "Citan": 0}
            self.target_count = 1
        def process_item(self, item):
            print(f"!!! ITEM VALIDADO Y PROCESADO: {item.model} - {item.url}")
            self.counts[item.model] += 1

    pipeline = MockPipeline()
    await scraper.scrape_for_pipeline(pipeline)

if __name__ == "__main__":
    asyncio.run(test())
