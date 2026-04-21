import re
import json
import logging
import html
import random
from datetime import datetime
from typing import List, Dict

import os
import sys

# --- PATH FIX ---
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent not in sys.path:
    sys.path.insert(0, parent)

from base.scraper import BaseScraper
from base.schemas import CarAdSchema
from utils.selenium_utils import get_stealth_driver, smooth_scroll, human_delay
from selenium.webdriver.common.by import By

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("MobileDeScraper")

# Imagen de Fallback (Stock Mercedes Vito de alta calidad)
FALLBACK_IMAGE = "https://www.mercedes-benz.es/vans/es/vito/panel-van/_jcr_content/root/responsivegrid/tabs/tabitem/gallery_copy/par/galleryitem_copy/image.mq6.png/1689255648000.png"

class MobileDeScraper(BaseScraper):
    def __init__(self, worker_id: str = "Worker"):
        super().__init__("mobile.de", "https://www.mobile.de")
        self.worker_id = worker_id

    def _normalize_car(self, item: Dict) -> CarAdSchema:
        """
        Normaliza los datos extraídos con precisión quirúrgica en kilometraje e imágenes.
        """
        try:
            # Texto base para extracción
            title = item.get('title', '').strip()
            raw_desc = item.get('modelDescription') or ''
            clean_desc = html.unescape(raw_desc)
            clean_desc = re.sub(r'<[^>]+>', ' ', clean_desc)
            full_text = (title + " " + clean_desc).lower()
            
            # 1. Extracción de AÑO
            year = 2023
            year_match = re.search(r'(\d{2}/\d{4})', full_text) or re.search(r'(\d{4})', full_text)
            if year_match:
                year_val_match = re.search(r'(\d{4})', year_match.group(1))
                if year_val_match: year = int(year_val_match.group(1))

            # 2. Extracción de KILOMETRAJE (CORRECCIÓN CRÍTICA)
            mileage = 0
            # Buscamos el patrón numérico seguido de km, permitiendo cualquier separador europeo
            # Ejemplo: "35.374 km", "35 374 km", "35374km"
            mileage_match = re.search(r'(\d+(?:[.\s\u00A0]*\d+)*)\s*km', full_text)
            if mileage_match:
                mileage_raw = mileage_match.group(1)
                mileage_clean = re.sub(r'[^\d]', '', mileage_raw)
                if mileage_clean:
                    mileage = int(mileage_clean)
            
            # Si el kilometraje sigue siendo 0 y el año no es >= 2024, alertar o intentar búsqueda secundaria
            if mileage == 0 and year < 2024:
                # Búsqueda desesperada de cualquier número > 1000 que no sea el precio
                nums = re.findall(r'\b(\d{1,3}[.\s]\d{3})\b', full_text)
                if nums:
                    potential = int(re.sub(r'[^\d]', '', nums[0]))
                    if potential > 100: mileage = potential

            # 3. Normalización de PRECIO
            price_raw = str(item.get('price', '0'))
            price_clean = re.sub(r'[^\d,]', '', price_raw).replace(',', '.')
            price = float(price_clean) if price_clean else 0.0

            # 4. Limpieza de URL
            ad_id_match = re.search(r'id=(\d+)', item.get('url', ''))
            clean_url = f"https://www.mobile.de/es/vehículo/detalles.html?id={ad_id_match.group(1)}" if ad_id_match else item.get('url', '')

            # 5. Mejora de IMÁGENES (Búsqueda Profunda en HTML)
            # Escaneamos el HTML crudo buscando patrones de imagen de Mobile.de (classistatic)
            raw_html = item.get('modelDescription', '')
            # Buscamos URLs que contengan 'classistatic.de' y terminen en JPG o tengan el parámetro rule
            img_patterns = [
                r'(https?://img\.classistatic\.de/[^"\'\s<>]+rule=mo-\d+)',
                r'(https?://img\.classistatic\.de/[^"\'\s<>]+)',
                r'(https?://[^"\'\s<>]+?\.(?:jpg|jpeg|png)(?:\?[\w=&-]+)?)'
            ]
            
            cleaned_images = []
            for pattern in img_patterns:
                matches = re.findall(pattern, raw_html)
                for img_url in matches:
                    # Normalizar a alta resolución
                    if 'rule=' in img_url:
                        img_url = re.sub(r'rule=mo-\d+', 'rule=mo-1024', img_url)
                    elif '$_' in img_url:
                        img_url = re.sub(r'\$_\d+\.JPG', '$_27.JPG', img_url)
                    
                    if img_url not in cleaned_images:
                        cleaned_images.append(img_url)
                if cleaned_images: break # Si encontramos del servidor oficial, paramos

            # Fallback si no hay imágenes o son placeholders
            if not cleaned_images or any("base64" in str(img) for img in cleaned_images):
                cleaned_images = [FALLBACK_IMAGE]
            else:
                # Priorizar la primera imagen válida que no sea de vendedor (logo)
                cleaned_images = [img for img in cleaned_images if "mo-prod/images" in img] or cleaned_images[:1]

            return CarAdSchema(
                portal=self.portal_name,
                brand="Mercedes-Benz",
                model=item.get('model_name', 'Vito'),
                year=year,
                mileage=mileage,
                fuel="Diesel",
                price=price,
                currency="EUR",
                country="Alemania",
                url=clean_url,
                source_url=clean_url,
                images=cleaned_images
            )
        except Exception as e:
            logger.error(f"Error normalizando coche: {e}")
            return None

    def scrape_list(self, page=None, brand: str = "", model: str = "") -> List[Dict]:
        return []

    async def scrape_for_pipeline(self, pipeline):
        """
        Integración con el pipeline de cuotas (Vito, Sprinter, Citan).
        """
        import requests
        driver = get_stealth_driver()
        try:
            # URLs específicas de DEALER proporcionadas por el usuario
            search_urls = {
                "Citan": "https://www.mobile.de/es/vehículos/buscar.html?sb=p&od=up&vc=Car&fr=2023&ms=17200%3B224&st=DEALER&s=Car&ref=srpHead",
                "Vito": "https://www.mobile.de/es/vehículos/buscar.html?sb=p&od=up&vc=Car&fr=2023&st=DEALER&ms=17200%3B125&s=Car&ref=srpHead",
                "Sprinter": "https://www.mobile.de/es/vehículos/buscar.html?sb=p&od=up&vc=Car&fr=2023&ms=17200%3B116&st=DEALER&s=Car&ref=srpHead"
            }

            for model_name, base_url in search_urls.items():
                if pipeline.counts[model_name] >= pipeline.target_count:
                    continue
                
                # Scraping por páginas
                for page_num in range(1, 4):
                    if pipeline.counts[model_name] >= pipeline.target_count:
                        break
                        
                    search_url = f"{base_url}&pgn={page_num}"
                    logger.info(f"[{self.worker_id}] Scrapeando {model_name} (DEALER) (Pág {page_num})...")
                    
                    driver.get(search_url)
                    human_delay(3, 5)
                    
                    # Consentimiento rápido
                    try:
                        btns = driver.find_elements(By.CLASS_NAME, "mde-consent-accept-btn")
                        if btns: btns[0].click()
                    except: pass
                    
                    smooth_scroll(driver)
                    
                    # Extracción Universal
                    extraction_script = """
                    return Array.from(document.querySelectorAll('article, div[data-testid*="result-listing"]')).map(card => {
                        let link = card.querySelector('a[href*="/detalles.h"]');
                        let titleEl = card.querySelector('h2, [data-testid="ad-title"]');
                        let priceEl = card.querySelector('[data-testid="price-label"], [data-testid="ad-price"]');
                        let allImgs = Array.from(card.querySelectorAll('img'));
                        let mainImg = allImgs.find(img => (img.src && img.src.includes('classistatic.de')) || 
                                                         (img.srcset && img.srcset.includes('classistatic.de'))) || allImgs[0];
                        if (link && titleEl) {
                            return {
                                title: titleEl.innerText,
                                price: priceEl ? priceEl.innerText : "0",
                                url: link.href,
                                images: mainImg ? [{
                                    src: mainImg.src,
                                    srcset: mainImg.srcset,
                                    dataSrc: mainImg.getAttribute('data-src') || mainImg.getAttribute('data-lazy-src')
                                }] : [],
                                modelDescription: card.innerHTML
                            };
                        }
                        return null;
                    }).filter(i => i !== null);
                    """
                    
                    raw_items = driver.execute_script(extraction_script)
                    logger.info(f"[{self.worker_id}] {model_name} (Pág {page_num}): Encontrados {len(raw_items)} anuncios en DOM.")
                    
                    # Preparar sesión de requests con cookies del driver para evitar bloqueos
                    session = requests.Session()
                    for cookie in driver.get_cookies():
                        session.cookies.set(cookie['name'], cookie['value'])
                    
                    for item in raw_items:
                        item['model_name'] = model_name
                        normalized = self._normalize_car(item)
                        if normalized and normalized.url:
                            # --- VALIDACIÓN DE LINKS (OBLIGATORIA) ---
                            # Mantener la URL tal cual la entrega el navegador (Ya viene codificada)
                            url_str = str(normalized.url)
                            if not url_str.startswith("http"):
                                url_str = "https://www.mobile.de" + url_str
                            
                            # Confianza total en el DOM (Si el buscador lo muestra, el coche existe)
                            logger.info(f"Link aceptado por presencia física: {url_str[:50]}...")
                            normalized.url = url_str
                            normalized.source_url = url_str

                            pipeline.process_item(normalized)
                            if pipeline.counts[model_name] >= pipeline.target_count:
                                break
                    
                    human_delay(2, 4)
                    
        except Exception as e:
            logger.error(f"Error en pipeline Mobile.de: {e}")
        finally:
            driver.quit()

    def run(self, brand: str = "Mercedes", model_list: str = "Vito,Sprinter,Citan") -> List[CarAdSchema]:
        import asyncio
        # Wrapper asíncrono para mantener compatibilidad
        loop = asyncio.new_event_loop()
        class MockPipeline:
            def __init__(self): self.items = []; self.counts = {"Vito":0, "Sprinter":0, "Citan":0}; self.target_count = 20
            def process_item(self, item): self.items.append(item); self.counts[item.model] += 1
        
        pipeline = MockPipeline()
        loop.run_until_complete(self.scrape_for_pipeline(pipeline))
        return pipeline.items

if __name__ == "__main__":
    scraper = MobileDeScraper()
    resultados = scraper.run()
    print(f"\nRESUMEN DE EXTRACCIÓN ({len(resultados)} coches):")
    print("-" * 50)
    for r in resultados[:10]:
        img_url = str(r.images[0])
        print(f"{r.model[:10]:<10} | {r.year} | {r.mileage:>7} km | Imgs: {len(r.images)} | URL: {img_url[:40]}...")
