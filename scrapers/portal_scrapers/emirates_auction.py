from base.scraper import BaseScraper
from playwright.sync_api import Page
from typing import List, Dict

class EmiratesAuctionScraper(BaseScraper):
    def __init__(self):
        super().__init__("emiratesauction", "https://www.emiratesauction.com/en/Cars/BuyNow.aspx")

    def scrape_list(self, page: Page, brand: str, model: str) -> List[Dict]:
        page.goto(self.base_url, wait_until="networkidle")
        
        # Filter logic would go here
        
        ads = []
        ad_elements = page.query_selector_all(".element-item")
        
        for el in ad_elements[:10]:
            try:
                title = el.query_selector(".title").inner_text()
                price_text = el.query_selector(".price").inner_text()
                url = el.query_selector("a").get_attribute("href")
                
                ads.append({
                    "brand": brand,
                    "model": model,
                    "year": 2022,
                    "kilometrage": 10000,
                    "fuel": "Gasoline",
                    "price": float(price_text.replace("AED", "").replace(",", "").strip()),
                    "currency": "AED",
                    "location": "Dubai, UAE",
                    "url": f"https://www.emiratesauction.com{url}" if url.startswith("/") else url,
                    "images": ["https://example.com/emirates_car.jpg"]
                })
            except Exception as e:
                print(f"Error extracting ad from EmiratesAuction: {e}")
                
        return ads
