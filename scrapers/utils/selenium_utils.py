import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth

def get_stealth_driver():
    """
    Crea y devuelve un driver de Chrome con Selenium Stealth configurado.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    
    # Evasión de detección básica
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    
    stealth(driver,
        languages=["es-ES", "es"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    
    return driver

def human_delay(min_sec=2, max_sec=5):
    """Espera un tiempo aleatorio para simular comportamiento humano."""
    time.sleep(random.uniform(min_sec, max_sec))

def smooth_scroll(driver):
    """Simula un scroll humano para activar la carga de elementos perezosos."""
    driver.execute_script("window.scrollTo({top: document.body.scrollHeight / 3, behavior: 'smooth'});")
    human_delay(1, 2)
    driver.execute_script("window.scrollTo({top: (document.body.scrollHeight / 3) * 2, behavior: 'smooth'});")
    human_delay(1, 2)
    driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
    human_delay(1, 2)
    driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
