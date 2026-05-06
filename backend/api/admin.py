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

async def run_scraper_task():
    status_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scraper_status.log"))
    
    def log_status(message):
        with open(status_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
        print(f"[ADMIN] {message}")

    log_status("Iniciando tarea de scraping en segundo plano...")
    # Add scrapers directory to path to allow imports
    scrapers_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scrapers"))
    if scrapers_path not in sys.path:
        sys.path.append(scrapers_path)
    
    try:
        from run_scrapers import run_targeted_scraping
        await run_targeted_scraping()
        log_status("Tarea de scraping completada con éxito.")
    except Exception as e:
        log_status(f"ERROR ejecutando scrapers: {str(e)}")

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
