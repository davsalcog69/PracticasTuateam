import logging
from portal_scrapers.mobile_de import MobileDeScraper

logging.basicConfig(level=logging.INFO)

class MockPipeline:
    def __init__(self):
        self.counts = {"Vito": 0, "Sprinter": 0, "Citan": 0, "Serie 3": 0, "A4": 0, "Golf GTI": 0, "Golf R": 0}
        self.target_count = 1
    def process_item(self, item):
        print(f"\n--- PROCESSED ITEM ---")
        print(f"Model: {item.model}")
        print(f"Year: {item.year}")
        print(f"URL: {item.url}")
        print(f"Images: {len(item.images)}")
        # Check for accident keywords manually here to see if we missed any
        # full_text is not in the schema, but we can infer
        self.counts[item.model] += 1

async def debug():
    scraper = MobileDeScraper()
    pipeline = MockPipeline()
    await scraper.scrape_for_pipeline(pipeline)

if __name__ == "__main__":
    import asyncio
    asyncio.run(debug())
