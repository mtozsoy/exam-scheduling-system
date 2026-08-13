from sqlalchemy import select
from app.db.database import SessionLocal
from app.models.academic_calendar import AcademicCalendar

def test_calendar_model():
    db = SessionLocal()
    try:
        calendars = db.execute(select(AcademicCalendar)).scalars().all()
        print(f"Total calendars found: {len(calendars)}")
        for cal in calendars:
            print(f"ID: {cal.calendar_id}, Year: {cal.academic_year}, Semester: {cal.semester}, Type: {cal.exam_type}, Active: {cal.is_active}")
            print(f"Dates: {cal.start_date} to {cal.end_date}")
    finally:
        db.close()

if __name__ == "__main__":
    test_calendar_model()
