from typing import List, Type
from base.scraper import BaseScraper
from utils.api_client import APIClient

class scrapingEngine:
    """
    Orchestrates the execution of multiple scrapers.
    Handles registration, logging, and data persistence.
    """
    def __init__(self):
        self.scrapers: List[BaseScraper] = []
        self.api_client = APIClient()

    def register_scraper(self, scraper: BaseScraper):
        """
        Adds a scraper to the engine's list.
        """
        self.scrapers.append(scraper)

    def run_all(self, brand: str, model: str):
        """
        Executes all registered scrapers for a given car model.
        """
        for scraper in self.scrapers:
            print(f"Starting scraping on {scraper.portal_name} for {brand} {model}...")
            try:
                # 1. Scrape and Validate
                ads = scraper.run(brand, model)
                
                # 2. Persist to Backend
                print(f"Scraped {len(ads)} ads. Sending to API...")
                self.api_client.post_car_ads(ads)
                
            except Exception as e:
                print(f"Critical error running scraper {scraper.portal_name}: {e}")

if __name__ == "__main__":
    # Example usage:
    # engine = ScrapingEngine()
    # engine.register_scraper(AutoScoutScraper())
    # engine.run_all("BMW", "Serie 3")
    pass
