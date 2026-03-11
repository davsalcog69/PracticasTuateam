class BaseScraper:
    """Base class for all car portal scrapers."""
    def __init__(self, portal_name):
        self.portal_name = portal_name
