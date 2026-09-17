from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.academic_calendar import AcademicCalendarResponse, AcademicCalendarCreate, AcademicCalendarUpdate
from app.services.academic_calendar_service import AcademicCalendarService

from app.api.deps import get_current_secretary_or_admin
from fastapi import Depends
router = APIRouter(dependencies=[Depends(get_current_secretary_or_admin)])
service = AcademicCalendarService()

@router.get("/academic-calendars", response_model=list[AcademicCalendarResponse])
def get_calendars(db: Session = Depends(get_db)):
    return service.get_all_calendars(db)

@router.get("/academic-calendars/active", response_model=list[AcademicCalendarResponse])
def get_active_calendars(db: Session = Depends(get_db)):
    return service.get_active_calendars(db)

@router.post("/academic-calendars", response_model=AcademicCalendarResponse)
def create_calendar(data: AcademicCalendarCreate, db: Session = Depends(get_db)):
    return service.create_calendar(db, data)

@router.put("/academic-calendars/{calendar_id}", response_model=AcademicCalendarResponse)
def update_calendar(calendar_id: int, data: AcademicCalendarUpdate, db: Session = Depends(get_db)):
    return service.update_calendar(db, calendar_id, data)

@router.delete("/academic-calendars/{calendar_id}")
def delete_calendar(calendar_id: int, db: Session = Depends(get_db)):
    return service.delete_calendar(db, calendar_id)
