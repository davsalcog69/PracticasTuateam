import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        page = await context.new_page()
        url = 'https://www.mobile.de/es/veh%C3%ADculos/buscar.html?isSearch=true&ms=3500%3B10%3B%3B%3B&s=Car&vc=Car'
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until='domcontentloaded')
        await asyncio.sleep(8) # Wait more for anti-bot
        
        # Take a screenshot to see if we are blocked
        await page.screenshot(path='scrapers/mobile_debug.png')
        
        # Get all div classes to find the card container
        divs = await page.evaluate("""() => {
            const all = document.querySelectorAll('div, a, article');
            return Array.from(all).slice(0, 100).map(el => ({
                tag: el.tagName,
                class: el.className,
                text: el.innerText.substring(0, 50)
            }));
        }""")
        
        import json
        with open('scrapers/dom_debug.json', 'w', encoding='utf-8') as f:
            json.dump(divs, f, indent=4, ensure_ascii=False)
            
        print(f"Debug saved. Screenshot at scrapers/mobile_debug.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
