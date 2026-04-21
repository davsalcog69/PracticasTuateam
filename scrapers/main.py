from engine import ScrapingEngine
# from portal_scrapers.autoscout24 import AutoScoutScraper

def main():
    engine = ScrapingEngine()
    # engine.register_scraper(AutoScoutScraper())
    # engine.run_all("BMW", "Serie 3")
    print("Scraper System initialized. Ready to add portal scrapers.")

if __name__ == "__main__":
    main()
