from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from api.schemas import CarSchema, ModelResponse, InspectionCreate, InspectionResponse, ProfitableCarResponse
from services.car_service import CarService
from services.inspection_service import InspectionService
from services.analysis_service import AnalysisService

router = APIRouter()
car_service = CarService()
inspection_service = InspectionService()
analysis_service = AnalysisService()

@router.get("/cars", response_model=List[CarSchema])
def get_cars(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return car_service.get_all_cars(db, skip=skip, limit=limit)

@router.get("/model/{brand}/{model}", response_model=ModelResponse)
def get_model_ads(brand: str, model: str, db: Session = Depends(get_db)):
    return car_service.get_cars_by_model(db, brand, model)

@router.post("/inspection-request", response_model=InspectionResponse)
def create_inspection_request(request: InspectionCreate, db: Session = Depends(get_db)):
    return inspection_service.create_inspection_request(db, request)

@router.get("/profitable-cars", response_model=List[ProfitableCarResponse])
def get_profitable_cars(db: Session = Depends(get_db)):
    return analysis_service.get_profitable_opportunities(db)
