import requests
from typing import List
from base.schemas import CarAdSchema

class APIClient:
    """
    Utility to send scraped data to the Backend API.
    """
    def __init__(self, base_api_url: str = "http://localhost:8000/api"):
        self.base_api_url = base_api_url

    def post_car_ads(self, ads: List[CarAdSchema]):
        """
        Sends a list of validated car ads to the backend.
        """
        endpoint = f"{self.base_api_url}/cars"
        # In a real scenario, this would loop or use a bulk endpoint
        for ad in ads:
            try:
                response = requests.post(endpoint, json=ad.dict())
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error sending ad {ad.url} to API: {e}")

    def create_scrape_run(self, portal_name: str, status: str = "STARTED"):
        """
        Logs a new scrape run in the database via the API.
        """
        # Implementation depends on the SCRAPE_RUNS table endpoint
        pass
