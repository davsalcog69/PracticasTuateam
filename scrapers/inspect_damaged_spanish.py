import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        # Search for damaged cars on mobile.de (Spanish)
        url = 'https://www.mobile.de/es/veh%C3%ADculos/buscar.html?isSearch=true&ms=3500%3B10%3B%3B%3B&q=da%C3%B1os&s=Car&vc=Car'
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until='networkidle')
        await asyncio.sleep(5)
        
        # Get all text and HTML content from the first 5 results
        results = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('article, div[data-testid*="result-listing"]')).slice(0, 5).map(card => {
                return {
                    text: card.innerText,
                    html: card.innerHTML
                };
            });
        }""")
        
        with open('scrapers/damaged_spanish_inspect.txt', 'w', encoding='utf-8') as f:
            for i, r in enumerate(results):
                f.write(f"--- RESULT {i} ---\n")
                f.write(f"TEXT:\n{r['text']}\n")
                f.write(f"HTML SNIPPET:\n{r['html'][:1000]}...\n\n")
            
        print(f"Done. Analyzed {len(results)} results. Saved to scrapers/damaged_spanish_inspect.txt")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
