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

# LISTA NEGRA COMPLETA DE ACCIDENTES Y DAÑOS
ACCIDENT_KEYWORDS = [
    # ACCIDENTES (DIRECTO)
    r'unfall', r'unfallschaden', r'unfallfahrzeug', r'schwerer unfall', r'totalschaden', r'unfallwagen', 
    r'frontschaden', r'heckschaden', r'seitenschaden',
    r'accidente', r'siniestro', r'coche accidentado', r'golpe frontal', r'golpe trasero', r'golpe lateral', r'siniestro total',
    r'accident', r'accident damage', r'total loss', r'crash damage', r'front damage', r'rear damage', r'side damage',
    
    # DAÑOS GENERALES
    r'beschädigt', r'schaden', r'vorschaden', r'altschaden', r'beschädigungen', r'mängel',
    r'dañado', r'daños', r'daños previos', r'defectos', r'desperfectos',
    r'damaged', r'damage', r'previous damage', r'defects', r'issues',
    
    # DAÑOS MECÁNICOS
    r'motorschaden', r'getriebeschaden', r'turboschaden', r'kupplung defekt', r'motor defekt', r'getriebe defekt',
    r'nicht fahrbereit', r'bedingt fahrbereit',
    r'motor roto', r'avería', r'caja de cambios rota', r'embrague roto', r'no arranca', r'no funciona', r'no circula',
    r'engine damage', r'engine failure', r'gearbox damage', r'transmission issue', r'not working', r'not drivable', r'broken',
    
    # COCHES PROBLEMÁTICOS
    r'bastlerfahrzeug', r'exportfahrzeug', r'händlerexport', r'ohne garantie', r'nur für export', r'zum ausschlachten',
    r'para piezas', r'para exportación', r'sin garantía', r'solo exportación', r'para desguace', r'no apto', r'no circula', r'no arranca',
    r'for parts', r'export only', r'no warranty', r'salvage', r'scrap',
    
    # REPARACIONES / SOSPECHOSO
    r'repariert', r'instandgesetzt', r'nachlackiert', r'neu lackiert', r'lackschaden', r'karosserieschaden', 
    r'rahmenschaden', r'instandsetzung',
    r'reparado', r'repintado', r'pintura nueva', r'daño de carrocería', r'daño estructural', r'vehículo siniestrado',
    r'repaired', r'repainted', r'body repair', r'frame damage', r'structural damage',
    
    # DESGASTE / ESTADO MALO
    r'stark gebraucht', r'verschlissen', r'abgenutzt', r'gebrauchsspuren', r'starke gebrauchsspuren',
    r'muy usado', r'desgastado', r'desgaste alto', r'marcas de uso', r'con daños', r'estado malo',
    r'heavily used', r'worn', r'wear and tear', r'signs of use',
    
    # EXPRESIONES ENGAÑOSAS
    r'leichte mängel', r'optische mängel', r'kleine schäden', r'altersbedingt', r'dem alter entsprechend',
    r'pequeños defectos', r'detalles estéticos', r'acorde a la edad', r'desgaste normal',
    r'minor defects', r'cosmetic issues', r'age related', r'small issues'
]

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

            # --- LÓGICA DE FILTRADO AVANZADO (FREITEXT, TÜV, OWNERS) ---
            model_category = item.get('model_name', '')
            
            # --- DETERMINACIÓN DEL ESTADO DEL VEHÍCULO (CRÍTICO) ---
            # EXTRAER EL VALOR LITERAL DE MOBILE.DE
            specs = item.get('specs', [])
            status_text_original = " ".join(specs).strip()
            status_text = status_text_original.lower()
            logger.info(f"--- DEBUG {title} specs: {status_text} ---")
            
            # El usuario quiere ver en vehicle_status la cadena que se utiliza para evaluar
            vehicle_status = status_text_original if status_text_original else "Gebrauchtfahrzeug"
            if len(vehicle_status) > 150:
                vehicle_status = vehicle_status[:147] + "..."
                
            # --- VALIDACIÓN INTERNA (vehicle_status_check) ---
            vehicle_status_check = "Dudoso" # Por defecto
            
            is_explicitly_clean = re.search(r'\b(unfallfrei|kein unfallschaden|sin accidentes|libre de accidentes)\b', status_text + " " + full_text)
            
            # Preparar texto para buscar daños: eliminar términos limpios para evitar falsos positivos (ej. 'unfall' coincidiendo con 'unfallfrei')
            text_for_damage_check = status_text + " " + full_text
            clean_phrases = [r'\bunfallfrei\b', r'\bkein unfallschaden\b', r'\bsin accidentes\b', r'\blibre de accidentes\b']
            for cp in clean_phrases:
                text_for_damage_check = re.sub(cp, '', text_for_damage_check, flags=re.IGNORECASE)
            
            # Buscar palabras clave de daño real
            has_damage_keywords = False
            matched_damage_kw = ""
            for kw in ACCIDENT_KEYWORDS:
                # Usar límites de palabra para keywords cortas y evitar coincidencias parciales (ej. 'schaden' en otras palabras)
                pattern = r'\b' + kw + r'\b' if len(kw) <= 7 else kw
                if re.search(pattern, text_for_damage_check, re.IGNORECASE):
                    has_damage_keywords = True
                    matched_damage_kw = kw
                    break
            
            if has_damage_keywords:
                logger.info(f"BLOQUEO TOTAL: Daño detectado en {title}. Keyword exacta: '{matched_damage_kw}'")
                vehicle_status_check = "Descartado"
            elif is_explicitly_clean:
                vehicle_status_check = "OK"
            else:
                logger.info(f"PRECAUCIÓN: No se confirma explícitamente 'Unfallfrei' en {title}. Se marca como Dudoso.")
                vehicle_status_check = "Dudoso"

            # El usuario pide ELIMINAR los dañados del dashboard.
            # En la DB de cars los dejamos como "Descartado", pero el ComparisonEngine los purgará.
            if vehicle_status_check == "Descartado":
                logger.info(f"Coche {title} marcado como DESCARTADO. No pasará a car_export.")
                
            brand_mapped = "Unknown"
            model_mapped = "Unknown"
            fuel_mapped = "Gasolina" if "benzin" in full_text else ("Diesel" if "diesel" in full_text else "Unknown")
            
            # --- Reglas para Premium Models ---
            if model_category in ["Serie 3", "A4", "Golf GTI", "Golf R"]:
                # Transmisión Manual - Descarte para estos modelos premium
                if re.search(r'\b(schaltgetriebe|manual)\b', full_text):
                    logger.debug(f"Descartado por transmisión manual: {title}")
                    return None
                    
                # TV y Propietarios (Vorbesitzer)
                has_tuv = bool(re.search(r'\b(hu neu|tüv neu|hu\s*\d{2}/\d{4}|tüv\s*\d{2}/\d{4})\b', full_text))
                owners_match = re.search(r'(\d+)\s*(?:fahrzeughalter|vorbesitzer)', full_text)
                owners = int(owners_match.group(1)) if owners_match else 0
                
                # Segn instruccin: "Si no hay info de TV: Marcar como dudoso o descartar"
                # Para evitar descartar TODO en el listado (donde no siempre sale), seremos ms laxos:
                # Solo descartamos si HAY info y es mala, o si el usuario prefiere volumen. 
                # Decidimos permitir si NO hay info para no vaciar el marketplace.
                
                if owners > 2:
                    logger.debug(f"Descartado: Demasiados dueños ({owners}): {title}")
                    return None

            
            if model_category == "Serie 3":
                brand_mapped = "BMW"
                model_mapped = "Serie 3"
                if not re.search(r'\b(320i|330i|330d|m340i)\b', full_text):
                    return None
                # Freitext check
                required = [r'\bm sport\b', r'\bsportpaket\b', r'\bharman kardon\b', r'\bpanorama\b', r'\bled\b', r'\bsitzheizung\b', r'\bleder\b']
                # Bajamos a 1 para el listado, ya que el snippet es corto
                score = sum(1 for req in required if re.search(req, full_text))
                if score < 1: return None

            elif model_category == "A4":
                brand_mapped = "Audi"
                model_mapped = "A4"
                if re.search(r'\b(tdi.*16\d\s*g/km|bastuck|attraction)\b', full_text):
                    return None
                required = [r'\bs line\b', r'\bvirtual cockpit\b', r'\bpanoramadach\b', r'\bleder\b', r'\bmatrix led\b', r'\bnavi\b', r'\bquattro\b']
                score = sum(1 for req in required if re.search(req, full_text))
                if score < 1: return None

            elif model_category == "Golf GTI":
                brand_mapped = "Volkswagen"
                model_mapped = "Golf GTI"
                if re.search(r'\b(golf 7|vii|chiptuning|remap)\b', full_text):
                    return None
                required = [r'\bclubsport\b', r'\bperformance\b', r'\bharman kardon\b', r'\bdcc\b', r'\biq\.light\b']
                score = sum(1 for req in required if re.search(req, full_text))
                # Flexible score
                
            elif model_category == "Golf R":
                brand_mapped = "Volkswagen"
                model_mapped = "Golf R"
                if re.search(r'\b(golf 7|vii|chiptuning|remap)\b', full_text):
                    return None
                required = [r'\bakrapovic\b', r'\b20 jahre\b', r'\b4motion\b', r'\bnürburgring\b', r'\bdcc\b']
                score = sum(1 for req in required if re.search(req, full_text))
                if re.search(r'\b20 jahre\b', full_text):
                    model_mapped = "Golf R 20 Jahre" # High priority mark

            elif model_category in ["Vito", "Sprinter", "Citan"]:
                brand_mapped = "Mercedes-Benz"
                model_mapped = model_category
                # Las furgonetas no tienen reglas freitext tan estrictas como los deportivos
                
            return CarAdSchema(
                portal=self.portal_name,
                brand=brand_mapped,
                model=model_mapped,
                year=year,
                mileage=mileage,
                fuel=fuel_mapped,
                price=price,
                currency="EUR",
                country="Alemania",
                vehicle_status=vehicle_status,
                vehicle_status_check=vehicle_status_check,
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
            # URLs específicas y avanzadas (kein Unfallschaden = ud=0 implícito en la búsqueda normal, 
            # pero lo forzamos. tr=AUTOMATIC_GEAR, etc.)
            search_urls = {
                "Citan": "https://www.mobile.de/es/vehículos/buscar.html?sb=p&od=up&vc=Car&fr=2023&ms=17200%3B224&st=DEALER&s=Car&ud=0&ref=srpHead",
                "Vito": "https://www.mobile.de/es/vehículos/buscar.html?sb=p&od=up&vc=Car&fr=2023&st=DEALER&ms=17200%3B125&s=Car&ud=0&ref=srpHead",
                "Sprinter": "https://www.mobile.de/es/vehículos/buscar.html?sb=p&od=up&vc=Car&fr=2023&ms=17200%3B116&st=DEALER&s=Car&ud=0&ref=srpHead",
                "Serie 3": "https://www.mobile.de/es/vehículos/buscar.html?c=EstateCar&c=Limousine&fr=2019%3A2022&ft=PETROL&ml=%3A80000&ms=3500%3B10%3B%3B%3B&od=up&p=%3A35000&s=Car&sb=p&st=DEALER&tr=AUTOMATIC_GEAR&ud=0&vc=Car",
                "A4": "https://www.mobile.de/es/vehículos/buscar.html?c=EstateCar&c=Limousine&fr=2019%3A2022&ml=%3A75000&ms=1900%3B9%3B%3B%3B&od=up&p=%3A32000&s=Car&sb=p&st=DEALER&tr=AUTOMATIC_GEAR&ud=0&vc=Car",
                "Golf GTI": "https://www.mobile.de/es/vehículos/buscar.html?fr=2020%3A2023&ft=PETROL&ml=%3A60000&ms=25200%3B14%3B%3B%3B&od=up&p=%3A28000&pw=180%3A&s=Car&sb=p&ud=0&vc=Car",
                "Golf R": "https://www.mobile.de/es/vehículos/buscar.html?fr=2020%3A2023&ft=PETROL&ml=%3A60000&ms=25200%3B14%3B%3B%3B&od=up&p=%3A35000&pw=220%3A&s=Car&sb=p&ud=0&vc=Car"
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
                            // Capturamos la línea de especificaciones completa (Año, KM, Combustible, Potencia, Estado...)
                            let specsEl = card.querySelector('[data-testid="listing-details-attributes"]');
                            let specs = specsEl ? [specsEl.innerText] : [];
                            
                            return {
                                title: titleEl.innerText,
                                price: priceEl ? priceEl.innerText : "0",
                                url: link.href,
                                images: mainImg ? [{
                                    src: mainImg.src,
                                    srcset: mainImg.srcset,
                                    dataSrc: mainImg.getAttribute('data-src') || mainImg.getAttribute('data-lazy-src')
                                }] : [],
                                modelDescription: card.innerHTML,
                                specs: specs
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

                            # --- EXTRACCIÓN DE GALERÍA DE IMÁGENES (PÁGINA DETALLE) ---
                            try:
                                logger.info(f"[{self.worker_id}] Obteniendo galería completa de {url_str[:60]}...")
                                resp = session.get(url_str, timeout=10)
                                if resp.status_code == 200:
                                    detail_imgs = re.findall(r'(https?://img\.classistatic\.de/api/v1/mo-prod/images/[^"\'\s<>]+rule=mo-\d+)', resp.text)
                                    if detail_imgs:
                                        hires_imgs = [re.sub(r'rule=mo-\d+', 'rule=mo-1024', img) for img in detail_imgs]
                                        # Eliminar duplicados manteniendo el orden
                                        hires_imgs = list(dict.fromkeys(hires_imgs))
                                        
                                        if len(hires_imgs) > 0:
                                            normalized.images = hires_imgs
                                            
                                        # CONTROL DE CALIDAD: si tiene muy pocas fotos (1-2), marcar como dudoso
                                        if len(normalized.images) <= 2 and normalized.vehicle_status_check == "OK":
                                            normalized.vehicle_status_check = "Dudoso"
                                            logger.info(f"[{self.worker_id}] Coche rebajado a Dudoso por tener solo {len(normalized.images)} fotos.")
                            except Exception as e:
                                logger.warning(f"[{self.worker_id}] Error obteniendo galería para {url_str}: {e}")

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
