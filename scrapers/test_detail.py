import asyncio
import requests
import re
from utils.selenium_utils import get_stealth_driver

def test():
    driver = get_stealth_driver()
    try:
        driver.get("https://www.mobile.de/es/veh%C3%ADculos/buscar.html?sb=p&od=up&vc=Car&fr=2023&ms=17200%3B224&st=DEALER&s=Car&ud=0&ref=srpHead")
        import time
        time.sleep(5)
        
        # Get cookies
        session = requests.Session()
        session.headers.update({
            "User-Agent": driver.execute_script("return navigator.userAgent;")
        })
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])
            
        # Get first car link
        link = driver.execute_script("return document.querySelector('article a[href*=\"/detalles.h\"]').href;")
        print("Link:", link)
        
        # Fetch with session
        resp = session.get(link)
        print("Status:", resp.status_code)
        
        imgs = re.findall(r'(https?://img\.classistatic\.de/api/v1/mo-prod/images/[^"\'\s<>]+rule=mo-\d+)', resp.text)
        print(f"Found {len(imgs)} images")
        hires = list(dict.fromkeys([re.sub(r'rule=mo-\d+', 'rule=mo-1024', img) for img in imgs]))
        print(hires[:3])
    finally:
        driver.quit()

if __name__ == "__main__":
    test()
