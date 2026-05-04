import asyncio
import logging
import os
import sys

# Add current dir to path
sys.path.append(os.getcwd())

from scrapers.portal_scrapers.mobile_de import MobileDeScraper

# Setup logging to be very verbose
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("ScraperDebug")

class MockPipeline:
    def __init__(self):
        self.counts = {"BMW_3er": 0, "Audi_A4": 0, "Golf_GTI": 0, "Golf_R": 0}
        self.target_count = 5
        
    def process_item(self, item):
        model = item.model
        # Map back for count tracking
        p_key = None
        if "Serie 3" in model: p_key = "BMW_3er"
        elif "A4" in model: p_key = "Audi_A4"
        elif "GTI" in model: p_key = "Golf_GTI"
        elif "Golf R" in model: p_key = "Golf_R"
        
        if p_key:
            self.counts[p_key] += 1
            print(f"FOUND: {item.brand} {item.model} - {item.price}€ - {str(item.url)[:50]}...")
        else:
            print(f"SKIPPED (No mapping): {item.brand} {item.model}")

async def test_new_models():
    scraper = MobileDeScraper(worker_id="DebugWorker")
    pipeline = MockPipeline()
    
    # Override search_urls to only test new ones
    search_urls = {
        "BMW_3er": "https://www.mobile.de/es/vehículos/buscar.html?c=EstateCar&c=Limousine&fr=2019%3A2022&ft=PETROL&ml=%3A80000&ms=3500%3B10%3B%3B%3B&od=up&p=%3A35000&s=Car&sb=p&st=DEALER&tr=AUTOMATIC_GEAR&ud=0&vc=Car",
        "Audi_A4": "https://www.mobile.de/es/vehículos/buscar.html?c=EstateCar&c=Limousine&fr=2019%3A2022&ml=%3A75000&ms=1900%3B9%3B%3B%3B&od=up&p=%3A32000&s=Car&sb=p&st=DEALER&tr=AUTOMATIC_GEAR&ud=0&vc=Car",
        "Golf_GTI": "https://www.mobile.de/es/vehículos/buscar.html?fr=2020%3A2023&ft=PETROL&ml=%3A60000&ms=25200%3B14%3B%3B%3B&od=up&p=%3A28000&pw=180%3A&s=Car&sb=p&ud=0&vc=Car",
        "Golf_R": "https://www.mobile.de/es/vehículos/buscar.html?fr=2020%3A2023&ft=PETROL&ml=%3A60000&ms=25200%3B14%3B%3B%3B&od=up&p=%3A35000&pw=220%3A&s=Car&sb=p&ud=0&vc=Car"
    }
    
    # We'll just run a manual loop for debugging
    from scrapers.utils.selenium_utils import get_stealth_driver, human_delay, smooth_scroll
    from selenium.webdriver.common.by import By
    
    driver = get_stealth_driver()
    try:
        for model_name, url in search_urls.items():
            print(f"\n--- TESTING {model_name} ---")
            driver.get(url)
            human_delay(3, 5)
            
            # Consent
            try:
                btns = driver.find_elements(By.CLASS_NAME, "mde-consent-accept-btn")
                if btns: btns[0].click()
            except: pass
            
            smooth_scroll(driver)
            
            extraction_script = scraper.extraction_script if hasattr(scraper, 'extraction_script') else """
                    return Array.from(document.querySelectorAll('article, div[data-testid*="result-listing"]')).map(card => {
                        let link = card.querySelector('a[href*="/detalles.h"]');
                        let titleEl = card.querySelector('h2, [data-testid="ad-title"]');
                        let priceEl = card.querySelector('[data-testid="price-label"], [data-testid="ad-price"]');
                        let allImgs = Array.from(card.querySelectorAll('img'));
                        let mainImg = allImgs.find(img => (img.src && img.src.includes('classistatic.de')) || 
                                                         (img.srcset && img.srcset.includes('classistatic.de'))) || allImgs[0];
                        if (link && titleEl) {
                            return {
                                title: titleEl.innerText,
                                price: priceEl ? priceEl.innerText : "0",
                                url: link.href,
                                images: mainImg ? [{
                                    src: mainImg.src,
                                    srcset: mainImg.srcset,
                                    dataSrc: mainImg.getAttribute('data-src') || mainImg.getAttribute('data-lazy-src')
                                }] : [],
                                modelDescription: card.innerHTML
                            };
                        }
                        return null;
                    }).filter(i => i !== null);
            """
            
            raw_items = driver.execute_script(extraction_script)
            print(f"Items found in DOM: {len(raw_items)}")
            
            for item in raw_items:
                item['model_name'] = model_name
                # Mock the logger to see debug messages
                import logging
                scraper_logger = logging.getLogger("MobileDeScraper")
                scraper_logger.setLevel(logging.DEBUG)
                
                normalized = scraper._normalize_car(item)
                if normalized:
                    pipeline.process_item(normalized)
                else:
                    title = item.get('title', '').lower()
                    print(f"DISCARDED: {title}")
                    # The _normalize_car logic is complex, let's see what might be failing
                    # Re-run a bit of logic here to diagnose
                    raw_desc = item.get('modelDescription') or ''
                    import html, re
                    clean_desc = html.unescape(raw_desc)
                    clean_desc = re.sub(r'<[^>]+>', ' ', clean_desc)
                    full_text = (title + " " + clean_desc).lower()
                    
                    has_tuv = bool(re.search(r'\b(hu neu|tüv neu|hu\s*\d{2}/\d{4}|tüv\s*\d{2}/\d{4})\b', full_text))
                    owners_match = re.search(r'(\d+)\s*(?:fahrzeughalter|vorbesitzer)', full_text)
                    owners = int(owners_match.group(1)) if owners_match else 0
                    manual = bool(re.search(r'\b(schaltgetriebe|manual)\b', full_text))
                    
                    print(f"  - has_tuv: {has_tuv}")
                    print(f"  - owners: {owners}")
                    print(f"  - manual: {manual}")
                    if model_name == "BMW_3er":
                        required = [r'\bm sport\b', r'\bsportpaket\b', r'\bharman kardon\b', r'\bpanorama\b', r'\bled\b', r'\bsitzheizung\b', r'\bleder\b']
                        score = sum(1 for req in required if re.search(req, full_text))
                        print(f"  - score: {score}")
                    elif model_name == "Audi_A4":
                        required = [r'\bs line\b', r'\bvirtual cockpit\b', r'\bpanoramadach\b', r'\bleder\b', r'\bmatrix led\b', r'\bnavi\b', r'\bquattro\b']
                        score = sum(1 for req in required if re.search(req, full_text))
                        print(f"  - score: {score}")
                    elif "Golf" in model_name:
                        required = [r'\bclubsport\b', r'\bperformance\b', r'\bharman kardon\b', r'\bdcc\b', r'\biq\.light\b'] if "GTI" in model_name else [r'\bakrapovic\b', r'\b20 jahre\b', r'\b4motion\b', r'\bnürburgring\b', r'\bdcc\b']
                        score = sum(1 for req in required if re.search(req, full_text))
                        print(f"  - score: {score}")
                    
                    # Print a snippet of full_text to see what's there
                    print(f"  - Snippet: {full_text[:200]}...")
                    
    finally:
        driver.quit()

if __name__ == "__main__":
    asyncio.run(test_new_models())
