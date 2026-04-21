from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from core.database import get_db
from models.favorite import Favorite
from models.car_export import CarExport
from api.schemas import FavoriteResponse
from api.deps import get_current_user
from models.user import User

router = APIRouter()

from pydantic import BaseModel

class FavoriteCreate(BaseModel):
    car_id: str

@router.post("", response_model=FavoriteResponse)
def add_favorite(
    request: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    car_id = request.car_id
    # Check if car exists
    car = db.query(CarExport).filter(CarExport.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    # Check if already in favorites
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.car_id == car_id
    ).first()
    
    if existing:
        return existing
    
    new_favorite = Favorite(user_id=current_user.id, car_id=car_id)
    db.add(new_favorite)
    db.commit()
    
    # Return with car loaded
    return db.query(Favorite).options(joinedload(Favorite.car)).filter(Favorite.id == new_favorite.id).first()

@router.delete("")
def remove_favorite(
    car_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.car_id == car_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    db.delete(favorite)
    db.commit()
    return {"message": "Favorite removed"}

@router.get("", response_model=List[FavoriteResponse])
def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Favorite).options(joinedload(Favorite.car)).filter(Favorite.user_id == current_user.id).all()
