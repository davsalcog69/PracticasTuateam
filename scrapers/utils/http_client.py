import requests
from typing import Dict, Optional

class HTTPClient:
    """
    Managed HTTP requests to handle headers and common configurations.
    """
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
        }

    def get(self, url: str, params: Optional[Dict] = None) -> Optional[str]:
        """
        Performs a GET request and returns the HTML content.
        """
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"HTTP GET Error on {url}: {e}")
            return None
