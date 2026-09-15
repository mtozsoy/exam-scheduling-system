from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.invigilator import InvigilatorResponse, InvigilatorCreate, InvigilatorUpdate
from app.services.invigilator_service import InvigilatorService

router = APIRouter()


@router.get("/invigilators", response_model=list[InvigilatorResponse])
def get_invigilators(db: Session = Depends(get_db)):  # noqa: B008
    return InvigilatorService().get_all_invigilators(db)


@router.post("/invigilators", response_model=InvigilatorResponse)
def create_invigilator(invigilator_in: InvigilatorCreate, db: Session = Depends(get_db)):
    return InvigilatorService().create_invigilator(db, invigilator_in)


@router.put("/invigilators/{invigilator_id}", response_model=InvigilatorResponse)
def update_invigilator(invigilator_id: int, invigilator_in: InvigilatorUpdate, db: Session = Depends(get_db)):
    return InvigilatorService().update_invigilator(db, invigilator_id, invigilator_in)


@router.delete("/invigilators/{invigilator_id}")
def delete_invigilator(invigilator_id: int, db: Session = Depends(get_db)):
    return InvigilatorService().delete_invigilator(db, invigilator_id)
