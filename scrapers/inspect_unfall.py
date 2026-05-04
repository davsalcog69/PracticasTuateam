import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        # Search for damaged BMW Serie 3
        url = 'https://www.mobile.de/es/veh%C3%ADculos/buscar.html?isSearch=true&ms=3500%3B10%3B%3B%3B&q=Unfall&s=Car&vc=Car'
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until='networkidle')
        await asyncio.sleep(5)
        
        # Take screenshot of the first few results
        await page.screenshot(path='scrapers/unfall_search.png')
        
        # Dump HTML of the first card
        card_html = await page.evaluate("document.querySelector('article, div[data-testid*=\"result-listing\"]').outerHTML")
        with open('scrapers/card_unfall.html', 'w', encoding='utf-8') as f:
            f.write(card_html)
            
        print("Done. Screenshot saved to scrapers/unfall_search.png and HTML to scrapers/card_unfall.html")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
