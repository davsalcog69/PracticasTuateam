from portal_scrapers.coches_net import CochesNetScraper
from portal_scrapers.emirates_auction import EmiratesAuctionScraper
from utils.db_repository import ScraperRepository
import argparse

def main():
    parser = argparse.ArgumentParser(description="Run car scrapers.")
    parser.add_argument("--brand", default="BMW", help="Car brand to search")
    parser.add_argument("--model", default="Serie 3", help="Car model to search")
    args = parser.parse_args()

    repo = ScraperRepository()
    scrapers = [
        CochesNetScraper(),
        # EmiratesAuctionScraper()
    ]

    for scraper in scrapers:
        print(f"--- Running {scraper.portal_name} scraper ---")
        try:
            ads = scraper.run(args.brand, args.model)
            if ads:
                repo.save_cars(ads)
            else:
                print(f"No ads found for {scraper.portal_name}")
        except Exception as e:
            print(f"Scraper {scraper.portal_name} failed: {e}")

if __name__ == "__main__":
    main()
