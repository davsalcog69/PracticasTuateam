from sqlalchemy.orm import Session
from models.scrape_run import ScrapeRun
from datetime import datetime

class ScrapeRunRepository:
    def create_run(self, db: Session, portal: str):
        db_run = ScrapeRun(portal=portal, status="STARTED")
        db.add(db_run)
        db.commit()
        db.refresh(db_run)
        return db_run

    def update_run(self, db: Session, run_id: int, status: str, cars_scraped: int = 0, errors: str = None):
        db_run = db.query(ScrapeRun).filter(ScrapeRun.id == run_id).first()
        if db_run:
            db_run.status = status
            db_run.cars_scraped = cars_scraped
            db_run.errors = errors
            db.commit()
            db.refresh(db_run)
        return db_run
