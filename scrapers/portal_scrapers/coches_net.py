from base.scraper import BaseScraper
from playwright_stealth import stealth_sync
from playwright.sync_api import Page
from typing import List, Dict
import time

class CochesNetScraper(BaseScraper):
    def __init__(self):
        super().__init__("coches.net", "https://www.coches.net/segunda-mano/")

    def scrape_list(self, page: Page, brand: str, model: str) -> List[Dict]:
        search_url = f"{self.base_url}?makeId={brand}&modelId={model}"
        # Note: In a real scenario, we'd need to map brand/model names to IDs or use the text search
        page.goto(search_url, wait_until="networkidle")
        
        # Handle cookies if present
        try:
            page.click("button:has-text('Aceptar')", timeout=5000)
        except:
            pass

        ads = []
        # Simplified selector for demonstration. Real selectors change frequently.
        ad_elements = page.query_selector_all(".mt-CardAd")
        
        for el in ad_elements[:10]: # Limit for demo
            try:
                title = el.query_selector(".mt-CardAd-title").inner_text()
                price_text = el.query_selector(".mt-CardAd-price").inner_text()
                url = el.query_selector("a").get_attribute("href")
                
                # Normalize data
                ads.append({
                    "brand": brand,
                    "model": model,
                    "year": 2020, # Dummy for demo, extraction would be here
                    "kilometrage": 50000,
                    "fuel": "Gasolina",
                    "price": float(price_text.replace("€", "").replace(".", "").strip()),
                    "currency": "EUR",
                    "location": "España",
                    "url": f"https://www.coches.net{url}" if url.startswith("/") else url,
                    "images": ["https://example.com/car.jpg"]
                })
            except Exception as e:
                print(f"Error extracting ad from Coches.net: {e}")
                
        return ads
