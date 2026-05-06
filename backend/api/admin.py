from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.database import get_db
from api.deps import get_current_user
from models.user import User
from datetime import datetime
import asyncio
import os
import sys

router = APIRouter()

def run_scraper_task():
    # Fix for Playwright/Asyncio on Windows: ensure ProactorEventLoop is used
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    status_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scraper_status.log"))
    
    # Clear previous logs for a fresh start
    with open(status_file, "w", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando proceso de actualización total...\n")
        f.flush()

    original_stdout = sys.stdout

    def log_status(message):
        # Write to file and flush immediately for real-time visibility
        try:
            with open(status_file, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
                f.flush()
                os.fsync(f.fileno()) # Force write to disk
        except:
            pass
            
        # Write to original stdout to avoid recursion
        try:
            original_stdout.write(f"[ADMIN] {message}\n")
            original_stdout.flush()
        except:
            pass

    # Capture stdout to write to log file as well
    class LoggerWriter:
        def __init__(self, log_func):
            self.log_func = log_func
        def write(self, message):
            if message and message.strip():
                self.log_func(message.strip())
        def flush(self):
            pass

    sys.stdout = LoggerWriter(log_status)

    try:
        log_status("Iniciando tarea de scraping en segundo plano...")
        scrapers_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scrapers"))
        if scrapers_path not in sys.path:
            sys.path.append(scrapers_path)
        
        from run_scrapers import run_targeted_scraping
        # Run the async scraper in the current thread (which is a worker thread from BackgroundTasks)
        asyncio.run(run_targeted_scraping())
        log_status("Tarea de scraping completada con éxito.")
    except Exception as e:
        log_status(f"ERROR ejecutando scrapers: {str(e)}")
    finally:
        sys.stdout = original_stdout

@router.get("/scraper-logs")
async def get_scraper_logs(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    status_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scraper_status.log"))
    if not os.path.exists(status_file):
        return {"logs": "No hay logs disponibles."}
    
    try:
        # Read last 500 lines to keep performance high
        with open(status_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            logs = "".join(lines[-500:])
        return {"logs": logs}
    except Exception as e:
        return {"logs": f"Error leyendo logs: {str(e)}"}

@router.post("/reset-and-scrape")
async def reset_and_scrape(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de administrador para esta acción."
        )

    try:
        # 1. Clear database tables in specific order
        print("[ADMIN] Limpiando tablas de la base de datos...")
        db.execute(text("DELETE FROM car_export"))
        db.execute(text("DELETE FROM car_price_history"))
        db.execute(text("DELETE FROM cars"))
        db.commit()
        print("[ADMIN] Base de datos limpia.")

        # 2. Trigger scrapers in background
        background_tasks.add_task(run_scraper_task)

        return {"message": "Base de datos limpiada y scrapers iniciados en segundo plano. Este proceso puede tardar varios minutos."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la solicitud: {str(e)}"
        )
