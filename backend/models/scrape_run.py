from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from core.database import Base

class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    portal = Column(String, index=True)
    status = Column(String)  # STARTED, COMPLETED, FAILED
    cars_scraped = Column(Integer, default=0)
    errors = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), onupdate=func.now())
