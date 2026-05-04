import asyncio
import json
import re
import random
import time
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# --- PATH FIX ---
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent not in sys.path:
    sys.path.insert(0, parent)

from playwright.async_api import async_playwright, Page, BrowserContext
from playwright_stealth import Stealth

from base.scraper import BaseScraper
from base.schemas import CarAdSchema
from utils.db_repository import ScraperRepository

# --- CONFIGURATION ---
TOTAL_PAGES = 4500
RECYCLE_EVERY_N_PAGES = 20  # More frequent recycling for Phase 3
COOL_DOWN_MINUTES = 5       # Wait 5 mins if blocked
OUTPUT_FILE = "dataset_coches.jsonl"
STATE_FILE = "scraper_state.json"
BASE_URL = "https://www.coches.net"
PAGE_URL_TEMPLATE = "https://www.coches.net/segunda-mano/?pg={page}&st=1"

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
    r'para piezas', r'para exportación', r'sin garantía', r'solo exportación', r'para desguace',
    r'for parts', r'export only', r'no warranty', r'salvage', r'scrap',
    
    # REPARACIONES / SOSPECHOSO
    r'repariert', r'instandgesetzt', r'nachlackiert', r'neu lackiert', r'lackschaden', r'karosserieschaden', 
    r'rahmenschaden', r'instandsetzung',
    r'reparado', r'repintado', r'pintura nueva', r'daño de carrocería', r'daño estructural',
    r'repaired', r'repainted', r'body repair', r'frame damage', r'structural damage',
    
    # DESGASTE / ESTADO MALO
    r'stark gebraucht', r'verschlissen', r'abgenutzt', r'gebrauchsspuren', r'starke gebrauchsspuren',
    r'muy usado', r'desgastado', r'desgaste alto', r'marcas de uso',
    r'heavily used', r'worn', r'wear and tear', r'signs of use',
    
    # EXPRESIONES ENGAÑOSAS
    r'leichte mängel', r'optische mängel', r'kleine schäden', r'altersbedingt', r'dem alter entsprechend',
    r'pequeños defectos', r'detalles estéticos', r'acorde a la edad', r'desgaste normal',
    r'minor defects', r'cosmetic issues', r'age related', r'small issues'
]

# Professional Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("CochesNetScraper")

class CochesNetScraper(BaseScraper):
    """
    ULTIMATE Coches.net Scraper (Phase 3).
    Implements Adaptive Cooling, Randomized Environment Stealth, and Chrome Channel.
    Designed to survive hyper-aggressive Akamai detection.
    """

    def __init__(self, worker_id: str = "Worker"):
        super().__init__("coches.net", "https://www.coches.net/segunda-mano/")
        self.worker_id = worker_id
        self.extracted_count = 0
        self.pages_done = 0
        self.start_time = time.time()
        self.db_repo = ScraperRepository()

    def _load_state(self) -> int:
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f).get('last_page', 0)
            except Exception: pass
        return 0

    def _save_state(self, last_page: int):
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump({'last_page': last_page, 'timestamp': str(datetime.now())}, f)
        except Exception: pass

    async def _human_behavior(self, page: Page):
        """Advanced human mimicry: random hovers, clicks, and reading pauses."""
        try:
            # 1. Random hovers on some elements if available
            elements = await page.query_selector_all('article, [data-testid="listing-card"]')
            if elements:
                target = random.choice(elements[:5])
                box = await target.bounding_view_rect()
                if box:
                    await page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
                    await asyncio.sleep(random.uniform(0.5, 1.5))

            # 2. Random scrolling with "reading" pauses
            for _ in range(random.randint(1, 3)):
                scroll = random.randint(400, 1200)
                await page.evaluate(f"window.scrollBy(0, {scroll})")
                await asyncio.sleep(random.uniform(1.5, 3.5)) # Pause to "read"
                
            # 3. Micro-movements
            for _ in range(3):
                x, y = random.randint(0, 500), random.randint(0, 500)
                await page.mouse.move(x, y, steps=15)
                await asyncio.sleep(0.2)
        except Exception: pass

    def _extract_data_from_html(self, html: str) -> Optional[Dict]:
        pattern_nd = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match_nd = re.search(pattern_nd, html, re.DOTALL)
        if match_nd:
            try: return json.loads(match_nd.group(1))
            except Exception: pass
            
        pattern_ip = r'window\.__INITIAL_PROPS__\s*=\s*JSON\.parse\("(.*?)"\);'
        match_ip = re.search(pattern_ip, html, re.DOTALL)
        if match_ip:
            try:
                raw = match_ip.group(1)
                decoded = json.loads(f'"{raw}"')
                return json.loads(decoded)
            except Exception: pass
        return None

    def _transform_item(self, item: Dict) -> Optional[Dict]:
        try:
            brand = (item.get('makeTitle') or item.get('make') or 'Desconocido').strip()
            model = (item.get('modelTitle') or item.get('model') or 'Desconocido').strip()
            
            # --- STRICT FILTERING FOR PREMIUM & VAN MODELS ---
            brand_lower = brand.lower()
            model_lower = model.lower()
            title_lower = (item.get('title') or '').lower()
            
            # Canonical Mapping
            if "bmw" in brand_lower and ("serie 3" in model_lower or "3er" in model_lower or "320" in model_lower or "330" in model_lower or "m340" in model_lower):
                brand = "BMW"
                model = "Serie 3"
            elif "audi" in brand_lower and "a4" in model_lower:
                brand = "Audi"
                model = "A4"
            elif "volkswagen" in brand_lower and "golf" in model_lower:
                brand = "Volkswagen"
                if "gti" in title_lower or "gti" in model_lower:
                    model = "Golf GTI"
                elif " r " in f" {title_lower} " or " r " in f" {model_lower} " or "20 jahre" in title_lower:
                    model = "Golf R"
                else:
                    return None
            elif "mercedes" in brand_lower:
                brand = "Mercedes"
                if "vito" in model_lower: model = "Vito"
                elif "sprinter" in model_lower: model = "Sprinter"
                elif "citan" in model_lower: model = "Citan"
                else: return None
            else:
                return None

            # --- DETERMINACIÓN DEL ESTADO DEL VEHÍCULO (CRÍTICO) ---
            vehicle_status = "Dudoso" # Por defecto en coches.net ya que no tienen el badge unfallfrei tan claro
            
            # Si el anuncio menciona cualquier palabra de daño, marcar como DESCARTADO
            if any(re.search(kw, title_lower) for kw in ACCIDENT_KEYWORDS):
                logger.info(f"MARCADO COMO DESCARTADO (Coches.net): Daño detectado en {title_lower}")
                vehicle_status = "Descartado"
            elif "perfecto estado" in title_lower or "impecable" in title_lower:
                vehicle_status = "Sin accidentes"
            else:
                vehicle_status = "Dudoso"

            props = item.get('attributes', [])
            attrs = {a['name']: a['value'] for a in props if 'name' in a} if isinstance(props, list) else (props or {})
            loc_data = item.get('location', {})
            location = loc_data.get('mainProvince') or loc_data.get('city') or 'España'

            ad = {
                "portal": self.portal_name,
                "brand": brand,
                "model": model,
                "year": int(item.get('year', 0)),
            }
            
            # STRICT YEAR FILTERING based on target models
            if model == "Serie 3" and not (2019 <= ad["year"] <= 2022): return None
            if model == "A4" and not (2019 <= ad["year"] <= 2022): return None
            if "Golf" in model and not (2020 <= ad["year"] <= 2023): return None
            if model in ["Vito", "Sprinter", "Citan"] and ad["year"] < 2023: return None

            ad.update({
                "mileage": int(item.get('km', 0)),
                "fuel": item.get('fuelType') or attrs.get('fuelType', 'Desconocido'),
                "power": int(item.get('hp', 0)) or int(attrs.get('hp', 0)) or 0,
                "price": float(item.get('price', {}).get('amount', 0.0)) if isinstance(item.get('price'), dict) else float(item.get('price', 0.0)),
                "currency": "EUR",
                "country": "España",
                "location": location,
                "vehicle_status": vehicle_status,
                "url": item.get('url', ''),
                "source_url": item.get('url', ''),
                "images": [item.get('mainImage')] if item.get('mainImage') else []
            })
            if ad["url"] and ad["url"].startswith("/"):
                ad["url"] = f"{BASE_URL}{ad['url']}"
                ad["source_url"] = ad["url"]
            return ad
        except Exception: return None

    async def scrape_page(self, context: BrowserContext, page_num: int) -> List[CarAdSchema]:
        url = PAGE_URL_TEMPLATE.format(page=page_num)
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        
        try:
            logger.info(f"[{self.worker_id}] Analyzing page {page_num}...")
            # Phase 3: Slower loading for stealth
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(random.uniform(6, 12)) # Longer initial wait
            
            await self._human_behavior(page)
            await page.wait_for_load_state("networkidle", timeout=30000)
            
            content = await page.content()
            data = self._extract_data_from_html(content)
            
            if not data:
                if "Ups!" in content or "algo no va bien" in content or "verificación" in content:
                    logger.error(f"[{self.worker_id}] Page {page_num}: DETECTED by Akamai. Triggering Cool-down.")
                    return None # Signal detection to the chunk loop
                return []

            props = data.get('props', {}).get('pageProps', {}) or data
            results = props.get('initialResults', {}) or props.get('initialSearchResults', {})
            items = results.get('items', [])
            
            validated = []
            for item in items:
                processed = self._transform_item(item)
                if processed:
                    try: validated.append(CarAdSchema(**processed))
                    except Exception: pass
            
            logger.info(f"[{self.worker_id}] Page {page_num}: Extracted {len(validated)} items.")
            return validated
        except Exception as e:
            logger.error(f"[{self.worker_id}] Page {page_num} ERROR: {str(e)[:100]}")
            return [] # Regular error, don't signal detection
        finally:
            await page.close()

    async def _scrape_chunk(self, p, start: int, end: int) -> bool:
        """Processes a chunk. Returns True if finished successfully, False if blocked."""
        browser = None
        
        # Phase 3: Environment Randomization
        u_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        # Mandatory Chrome Channel for Legitimacy
        try:
            browser = await p.chromium.launch(
                headless=True,
                channel="chrome", # Use real Chrome
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
        except Exception:
            # Fallback to Chromium if Chrome is not installed
            logger.warning(f"[{self.worker_id}] Chrome channel not found, falling back to Chromium.")
            browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])

        try:
            context = await browser.new_context(
                user_agent=random.choice(u_agents),
                viewport={'width': random.randint(1280, 1920), 'height': random.randint(720, 1080)},
                locale="es-ES",
                timezone_id="Europe/Madrid"
            )

            # Deep Warmup
            warm = await context.new_page()
            await Stealth().apply_stealth_async(warm)
            await warm.goto("https://www.google.com", wait_until="domcontentloaded")
            await asyncio.sleep(random.uniform(4, 7))
            await warm.goto(BASE_URL, wait_until="domcontentloaded")
            await asyncio.sleep(random.uniform(8, 12))
            await warm.close()

            with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                for p_num in range(start, end + 1):
                    page_ads = await self.scrape_page(context, p_num)
                    
                    if page_ads is None: # Detection signaled
                        return False 
                    
                    if page_ads:
                        for ad in page_ads:
                            f.write(ad.model_dump_json() + '\n')
                        self.db_repo.save_cars(page_ads)
                        self.extracted_count += len(page_ads)
                    
                    self.pages_done += 1
                    self._save_state(p_num)
                    
                    # Log Progress
                    elapsed = time.time() - self.start_time
                    avg = elapsed / self.pages_done if self.pages_done > 0 else 0
                    eta = str(timedelta(seconds=int(avg * (TOTAL_PAGES - p_num))))
                    logger.info(f"[{self.worker_id}] P:{p_num}/{TOTAL_PAGES} | OK | Total:{self.extracted_count} | ETA:{eta}")
                    
                    if p_num < end:
                        # Stochastic Delays ~30s as requested
                        delay = random.uniform(25, 40)
                        logger.info(f"[{self.worker_id}] Delaying {delay:.1f}s for stealth...")
                        await asyncio.sleep(delay)
            
            return True
        except Exception as e:
            logger.error(f"[{self.worker_id}] Chunk process error: {e}")
            return False
        finally:
            try:
                if browser:
                    await browser.close()
            except Exception: pass

    async def scrape_all(self, start_page: int = 1, end_page: int = 4500):
        current_page = max(start_page, self._load_state() + 1)
        logger.info(f"[{self.worker_id}] ULTIMATE BYPASS MODE ACTIVATED. Resuming at page {current_page}...")

        while current_page <= end_page:
            chunk_end = min(current_page + RECYCLE_EVERY_N_PAGES - 1, end_page)
            logger.info(f"[{self.worker_id}] Launching Fresh Environment for pages {current_page}-{chunk_end}")
            
            async with async_playwright() as p:
                success = await self._scrape_chunk(p, current_page, chunk_end)
            
            if not success:
                # ADAPTIVE COOL DOWN
                logger.warning(f"[{self.worker_id}] DETECTED. Entering cool-down for {COOL_DOWN_MINUTES} minutes...")
                await asyncio.sleep(COOL_DOWN_MINUTES * 60)
                current_page = self._load_state() + 1 # Retry from last OK page
            else:
                current_page = chunk_end + 1
                # Small pause between chunks even if successful
                await asyncio.sleep(30)

        logger.info(f"[{self.worker_id}] Scrape complete. Total extracted: {self.extracted_count}")

    async def scrape_for_pipeline(self, pipeline):
        """Specialized mode for the 20-car-per-model pipeline."""
        logger.info(f"[{self.worker_id}] Starting Coches.net for targeted quota...")
        
        # Reset state for quick test mode
        self._save_state(0)
        
        # Target URLs for specific models with strict filters
        queries = {
            "Vito": "https://www.coches.net/mercedes-benz/vito/segunda-mano/?pg={page}&MinYear=2023",
            "Sprinter": "https://www.coches.net/mercedes-benz/sprinter/segunda-mano/?pg={page}&MinYear=2023",
            "Citan": "https://www.coches.net/mercedes-benz/citan/segunda-mano/?pg={page}&MinYear=2023",
            "Serie 3": "https://www.coches.net/bmw/serie_3/segunda-mano/?pg={page}&MinYear=2019&MaxYear=2022&MaxKms=80000",
            "A4": "https://www.coches.net/audi/a4/segunda-mano/?pg={page}&MinYear=2019&MaxYear=2022&MaxKms=75000",
            "Golf GTI": "https://www.coches.net/volkswagen/golf/segunda-mano/?pg={page}&MinYear=2020&MaxYear=2023&MaxKms=60000",
            "Golf R": "https://www.coches.net/volkswagen/golf/segunda-mano/?pg={page}&MinYear=2020&MaxYear=2023&MaxKms=60000"
        }

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, channel="chrome", args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                locale="es-ES"
            )

            for model_name, url_template in queries.items():
                if pipeline.counts[model_name] >= pipeline.target_count:
                    continue
                
                logger.info(f"[{self.worker_id}] Targeting {model_name} on Coches.net...")
                for current_page in range(1, 6): # Just a few pages per model
                    if pipeline.counts[model_name] >= pipeline.target_count:
                        break
                        
                    url = url_template.format(page=current_page)
                    # We can't use scrape_page directly because it uses PAGE_URL_TEMPLATE
                    # I'll create a temporary override or just use the logic
                    
                    page = await context.new_page()
                    await Stealth().apply_stealth_async(page)
                    try:
                        logger.info(f"[{self.worker_id}] Analyzing {model_name} page {current_page}...")
                        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                        await asyncio.sleep(random.uniform(4, 7))
                        
                        content = await page.content()
                        data = self._extract_data_from_html(content)
                        if data:
                            props = data.get('props', {}).get('pageProps', {}) or data
                            results = props.get('initialResults', {}) or props.get('initialSearchResults', {})
                            items = results.get('items', [])
                            
                            found_count = len(items)
                            processed_items = []
                            for item in items:
                                processed = self._transform_item(item)
                                if processed:
                                    processed_items.append(CarAdSchema(**processed))
                            
                            logger.info(f"[{self.worker_id}] [INFO] Página cargada correctamente")
                            logger.info(f"[{self.worker_id}] [INFO] Coches encontrados: {found_count}")
                            logger.info(f"[{self.worker_id}] [INFO] Filtrados y validados: {len(processed_items)}")

                            # Map the model mapped names back to the pipeline keys
                            for ad in processed_items:
                                pipeline.process_item(ad)
                                
                                if pipeline.counts[model_name] >= pipeline.target_count:
                                    break
                    except Exception as e:
                        logger.error(f"Error: {e}")
                    finally:
                        await page.close()

                    if not pipeline.is_finished():
                        await asyncio.sleep(random.uniform(5, 10))

            await browser.close()

    def scrape_list(self, page=None, brand: str = "", model: str = "") -> List[Dict]:
        return asyncio.run(self.scrape_all(1, 1))

    def run(self, brand: str = "", model: str = "", start_page: int = 1, end_page: int = 3) -> List[CarAdSchema]:
        return asyncio.run(self.scrape_all(start_page, end_page))

if __name__ == "__main__":
    crawler = CochesNetScraper()
    try:
        asyncio.run(crawler.scrape_all(1, TOTAL_PAGES))
    except KeyboardInterrupt:
        logger.info("Process stopped by user.")
