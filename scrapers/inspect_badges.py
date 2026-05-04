import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        # Search for BMW 3 (Spanish)
        url = 'https://www.mobile.de/es/veh%C3%ADculos/buscar.html?isSearch=true&ms=3500%3B10%3B%3B%3B&s=Car&vc=Car'
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until='networkidle')
        await asyncio.sleep(5)
        
        # Get all text and HTML content from the first 5 results
        data = await page.evaluate("""() => {
            const cards = Array.from(document.querySelectorAll('article'));
            return cards.slice(0, 3).map(card => {
                const spans = Array.from(card.querySelectorAll('span, div'));
                const statusBadges = spans.filter(s => 
                    s.innerText.toLowerCase().includes('accidente') || 
                    s.innerText.toLowerCase().includes('daño') ||
                    s.innerText.toLowerCase().includes('unfall') ||
                    s.innerText.toLowerCase().includes('schaden')
                ).map(s => ({
                    tag: s.tagName,
                    class: s.className,
                    text: s.innerText
                }));
                
                return {
                    title: card.querySelector('h2')?.innerText,
                    all_text: card.innerText,
                    statusBadges: statusBadges
                };
            });
        }""")
        
        import json
        with open('scrapers/badge_inspect.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"Done. Saved to scrapers/badge_inspect.json")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
