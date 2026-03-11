from abc import ABC, abstractmethod
from typing import List, Dict
from playwright.sync_api import sync_playwright, Page, Browser
from playwright_stealth import stealth_sync
from base.schemas import CarAdSchema
import time

class BaseScraper(ABC):
    def __init__(self, portal_name: str, base_url: str):
        self.portal_name = portal_name
        self.base_url = base_url
        self.browser: Browser = None
        self.playwright = None

    def start_browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        return self.browser

    def stop_browser(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def get_page(self) -> Page:
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        stealth_sync(page)
        return page

    @abstractmethod
    def scrape_list(self, page: Page, brand: str, model: str) -> List[Dict]:
        pass

    def run(self, brand: str, model: str) -> List[CarAdSchema]:
        self.start_browser()
        page = self.get_page()
        validated_ads = []
        try:
            raw_ads = self.scrape_list(page, brand, model)
            for raw_ad in raw_ads:
                try:
                    raw_ad['portal'] = self.portal_name
                    validated_ads.append(CarAdSchema(**raw_ad))
                except Exception as e:
                    print(f"Validation error for ad {raw_ad.get('url')}: {e}")
        finally:
            self.stop_browser()
        return validated_ads
