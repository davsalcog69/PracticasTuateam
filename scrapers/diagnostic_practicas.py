import os
import sys
import json

# Add parent directory to path to find utils
scrapers_dir = os.path.dirname(os.path.abspath(__file__))
if scrapers_dir not in sys.path:
    sys.path.append(scrapers_dir)

from portal_scrapers.mobile_de import MobileDeScraper
from utils.selenium_utils import get_stealth_driver, human_delay, smooth_scroll
from selenium.webdriver.common.by import By

def diagnostic():
    driver = get_stealth_driver()
    try:
        url = "https://www.mobile.de/es/veh%C3%ADculos/buscar.html?vc=Car&ms=17200;125;;&fr=2023"
        driver.get(url)
        human_delay(5, 7)
        
        # Bypass Consent
        try:
            consent_btn = driver.find_elements(By.CLASS_NAME, "mde-consent-accept-btn")
            if consent_btn:
                consent_btn[0].click()
                human_delay(1, 2)
        except: pass
        
        smooth_scroll(driver)
        
        # Capture raw cards
        cards = driver.execute_script("""
            return Array.from(document.querySelectorAll('article, [data-testid="result-listing"]')).map(card => ({
                html: card.innerHTML,
                innerText: card.innerText,
                img: Array.from(card.querySelectorAll('img')).map(img => ({
                    src: img.src,
                    dataSrc: img.getAttribute('data-src'),
                    srcset: img.srcset
                }))
            }));
        """)
        
        with open("diagnostic_elements.json", "w", encoding="utf-8") as f:
            json.dump(cards[:3], f, indent=2)
        
        print(f"Captured {len(cards)} cards for analysis.")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    diagnostic()
