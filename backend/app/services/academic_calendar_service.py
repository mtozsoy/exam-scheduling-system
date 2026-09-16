from sqlalchemy import select, update
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.academic_calendar import AcademicCalendar
from app.schemas.academic_calendar import AcademicCalendarCreate, AcademicCalendarUpdate

class AcademicCalendarService:
    def get_all_calendars(self, db: Session) -> list[AcademicCalendar]:
        return list(db.scalars(select(AcademicCalendar)).all())

    def get_active_calendars(self, db: Session) -> list[AcademicCalendar]:
        return list(db.scalars(select(AcademicCalendar).where(AcademicCalendar.is_active == True)).all())

    def _deactivate_others(self, db: Session, exam_type: str, exclude_id: int):
        # Eğer bir takvim aktif ediliyorsa, aynı exam_type için diğer aktif olanlar pasif olmalı
        db.execute(
            update(AcademicCalendar)
            .where(AcademicCalendar.exam_type == exam_type, AcademicCalendar.calendar_id != exclude_id)
            .values(is_active=False)
        )
        db.commit()

    def create_calendar(self, db: Session, data: AcademicCalendarCreate) -> AcademicCalendar:
        new_cal = AcademicCalendar(
            academic_year=data.academic_year,
            semester=data.semester,
            exam_type=data.exam_type,
            start_date=data.start_date,
            end_date=data.end_date,
            is_active=data.is_active
        )
        db.add(new_cal)
        db.commit()
        db.refresh(new_cal)

        if new_cal.is_active:
            self._deactivate_others(db, new_cal.exam_type, new_cal.calendar_id)
            db.refresh(new_cal)
            
        return new_cal

    def update_calendar(self, db: Session, calendar_id: int, data: AcademicCalendarUpdate) -> AcademicCalendar:
        cal = db.execute(select(AcademicCalendar).where(AcademicCalendar.calendar_id == calendar_id)).scalars().first()
        if not cal:
            raise HTTPException(status_code=404, detail="Akademik takvim bulunamadı.")

        if data.academic_year is not None:
            cal.academic_year = data.academic_year
        if data.semester is not None:
            cal.semester = data.semester
        if data.exam_type is not None:
            cal.exam_type = data.exam_type
        if data.start_date is not None:
            cal.start_date = data.start_date
        if data.end_date is not None:
            cal.end_date = data.end_date
        
        was_inactive = not cal.is_active
        if data.is_active is not None:
            cal.is_active = data.is_active

        db.commit()
        db.refresh(cal)

        if cal.is_active:
            self._deactivate_others(db, cal.exam_type, cal.calendar_id)
            db.refresh(cal)

        return cal

    def delete_calendar(self, db: Session, calendar_id: int) -> dict:
        cal = db.execute(select(AcademicCalendar).where(AcademicCalendar.calendar_id == calendar_id)).scalars().first()
        if not cal:
            raise HTTPException(status_code=404, detail="Akademik takvim bulunamadı.")
            
        if cal.is_active:
            raise HTTPException(status_code=409, detail="Aktif durumdaki bir takvim silinemez. Önce pasife çekmelisiniz.")

        db.delete(cal)
        db.commit()
        return {"success": True, "message": "Akademik takvim başarıyla silindi."}
