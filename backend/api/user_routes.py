from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from core.database import get_db
from api.deps import get_current_user
from api.user_schemas import UserOut, UserUpdate, PasswordUpdate, RecentCarOut, UserCreate
from models.user import User, UserActivity
from core.security import get_password_hash, verify_password
from typing import List

router = APIRouter()

@router.get("/me", response_model=UserOut)
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/update", response_model=UserOut)
def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    
    if user_in.avatar is not None:
        # Validation for allowed emojis
        allowed_emojis = ['😀', '😎', '🚗', '🔥', '⭐']
        if user_in.avatar not in allowed_emojis:
            raise HTTPException(status_code=400, detail="Avatar no válido")
        current_user.avatar = user_in.avatar
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/password")
def update_password_me(
    password_in: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(password_in.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Mala contraseña actual")
    
    current_user.hashed_password = get_password_hash(password_in.new_password)
    db.commit()
    return {"message": "Contraseña actualizada correctamente"}

@router.post("/record-visit/{car_id}")
def record_visit(
    car_id: str,
    model_name: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    visits_count = db.query(UserActivity).filter(UserActivity.user_id == current_user.id).count()
    if visits_count >= 20:
        oldest = db.query(UserActivity).filter(UserActivity.user_id == current_user.id).order_by(UserActivity.viewed_at.asc()).first()
        db.delete(oldest)

    new_visit = UserActivity(
        user_id=current_user.id,
        car_id=car_id,
        model_name=model_name
    )
    db.add(new_visit)
    db.commit()
    return {"status": "recorded"}

@router.get("/recent-cars", response_model=List[RecentCarOut])
def get_recent_cars(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(UserActivity).filter(UserActivity.user_id == current_user.id).order_by(UserActivity.viewed_at.desc()).all()

# Admin Routes
@router.post("/admin/create-user", response_model=UserOut)
def admin_create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permisos insuficientes. Solo administradores.")
    
    existing_user = db.query(User).filter(User.username == user_in.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe.")
    
    new_user = User(
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_admin=user_in.is_admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
