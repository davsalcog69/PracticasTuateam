from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from api.schemas import CarSchema, ModelResponse, InspectionCreate, InspectionResponse, ProfitableCarResponse, ExportedCarResponse
from services.car_service import CarService
from services.inspection_service import InspectionService
from services.analysis_service import AnalysisService
from api.deps import get_current_user

# Auth & User Routes
from api.auth import router as auth_router
from api.user_routes import router as user_router
from api.favorite_routes import router as favorite_router
<<<<<<< HEAD
=======
from api.admin import router as admin_router
>>>>>>> development

router = APIRouter()
# ... (existing service instantiations)
car_service = CarService()
inspection_service = InspectionService()
analysis_service = AnalysisService()

# Protected Routes (Require Login)
@router.get("/cars", response_model=List[CarSchema])
def get_cars(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return car_service.get_all_cars(db, skip=skip, limit=limit)

@router.get("/cars/export", response_model=ExportedCarResponse)
def get_exported_cars(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return car_service.get_exported_cars(db, skip=skip, limit=limit)

@router.get("/model/{brand}/{model}", response_model=ModelResponse)
def get_model_ads(
    brand: str, 
    model: str, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return car_service.get_cars_by_model(db, brand, model)

@router.post("/inspection-request", response_model=InspectionResponse)
def create_inspection_request(
    request: InspectionCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return inspection_service.create_inspection_request(db, request)

@router.get("/profitable-cars", response_model=List[ProfitableCarResponse])
def get_profitable_cars(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return analysis_service.get_profitable_opportunities(db)

# Registration of New Routers
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(user_router, prefix="/user", tags=["user"])
router.include_router(favorite_router, prefix="/favorites", tags=["favorites"])
<<<<<<< HEAD
=======
router.include_router(admin_router, prefix="/admin", tags=["admin"])
>>>>>>> development
