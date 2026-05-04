"""
Debug script: Extract raw HTML from mobile.de search cards to find where
the vehicle status information lives (e.g., 'Con daños', 'Vehículo siniestrado', etc.)
"""
import time
import json
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPERS_ROOT = os.path.join(ROOT, "scrapers")
sys.path.insert(0, ROOT)
sys.path.insert(0, SCRAPERS_ROOT)

from utils.selenium_utils import get_stealth_driver, smooth_scroll, human_delay

def main():
    driver = get_stealth_driver()
    try:
        # Use a URL that we KNOW has damaged cars (no ud=0 filter)
        url = "https://www.mobile.de/es/veh%C3%ADculos/buscar.html?ms=3500%3B10%3B%3B%3B&s=Car&vc=Car&sb=p&od=up"
        print(f"Navigating to: {url}")
        driver.get(url)
        human_delay(3, 5)
        
        # Accept cookies
        try:
            btns = driver.find_elements("class name", "mde-consent-accept-btn")
            if btns: btns[0].click()
            human_delay(1, 2)
        except: pass
        
        smooth_scroll(driver)
        
        # Extract the FULL innerHTML of the first 3 cards
        script = """
        return Array.from(document.querySelectorAll('article, div[data-testid*="result-listing"]')).slice(0, 3).map((card, idx) => {
            let allText = card.innerText;
            let allSpans = Array.from(card.querySelectorAll('span, div, p, li')).map(el => ({
                tag: el.tagName,
                class: el.className.substring(0, 80),
                text: el.innerText.substring(0, 200),
                testid: el.getAttribute('data-testid') || ''
            }));
            return {
                index: idx,
                fullText: allText.substring(0, 2000),
                elements: allSpans
            };
        });
        """
        
        results = driver.execute_script(script)
        
        with open('scrapers/card_deep_inspect.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nExtracted {len(results)} cards. Saved to scrapers/card_deep_inspect.json")
        
        # Print a summary
        for card in results:
            print(f"\n--- CARD {card['index']} ---")
            print(f"FULL TEXT:\n{card['fullText'][:500]}")
            print(f"\nELEMENTS WITH 'accidente' OR 'daño' OR 'siniestro' OR 'ocasión':")
            for el in card['elements']:
                t = el['text'].lower()
                if any(kw in t for kw in ['accidente', 'daño', 'siniestro', 'ocasión', 'circular', 'condicion']):
                    print(f"  [{el['tag']}] class={el['class'][:40]} testid={el['testid']} => {el['text']}")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
