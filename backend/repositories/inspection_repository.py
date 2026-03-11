import uuid
from sqlalchemy.orm import Session
from models.inspection import InspectionRequest
from api.schemas import InspectionCreate

class InspectionRepository:
    def create_request(self, db: Session, request: InspectionCreate):
        db_request = InspectionRequest(
            id=str(uuid.uuid4()),
            car_id=request.car_id,
            user_name=request.user_name,
            user_email=request.user_email,
            user_phone=request.user_phone,
            notes=request.notes
        )
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        return db_request

    def get_requests(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(InspectionRequest).offset(skip).limit(limit).all()
