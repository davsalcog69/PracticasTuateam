
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def test_url():
    url = "https://www.mobile.de/es/veh%C3%ADculo/detalles.html?id=451934349"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("https://www.mobile.de/es/buscar-vehiculo.html") # Pre-load to get session
        time.sleep(3)
        
        # Test 1: Requests
        res = requests.get(url, headers={"User-Agent": driver.execute_script("return navigator.userAgent;")})
        print(f"Requests status: {res.status_code}")
        
        # Test 2: Browser fetch (Accented)
        status = driver.execute_script("""
            return fetch(arguments[0], { method: 'HEAD' })
                .then(r => r.status)
                .catch(e => -1);
        """, url)
        print(f"Browser fetch HEAD status (Accented): {status}")

        # Test 2b: Browser fetch (Non-accented)
        url_non_accented = url.replace("veh%C3%ADculo", "vehiculo")
        status_non = driver.execute_script("""
            return fetch(arguments[0], { method: 'HEAD' })
                .then(r => r.status)
                .catch(e => -1);
        """, url_non_accented)
        print(f"Browser fetch HEAD status (Non-accented): {status_non}")

        # Test 6: Specific "vehiculo" (no accent) test
        url_broken = url.replace("veh%C3%ADculo", "vehiculo")
        status_broken = driver.execute_script("""
            return fetch(arguments[0], { method: 'HEAD' })
                .then(r => r.status)
                .catch(e => -1);
        """, url_broken)
        print(f"Browser fetch status for NO-ACCENT URL: {status_broken}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_url()
