from sqlalchemy.orm import Session
from repositories.inspection_repository import InspectionRepository
from api.schemas import InspectionCreate

class InspectionService:
    def __init__(self):
        self.repository = InspectionRepository()

    def create_inspection_request(self, db: Session, request: InspectionCreate):
        return self.repository.create_request(db, request)

    def get_all_inspection_requests(self, db: Session, skip: int = 0, limit: int = 100):
        return self.repository.get_requests(db, skip, limit)
