from fastapi import FastAPI
from api.routes import router as api_router
from core.database import engine, Base
from models.car import Car
from models.inspection import InspectionRequest
from models.scrape_run import ScrapeRun

# Create database tables (if they don't exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Car Import AI API")

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Car Import AI API is online"}
