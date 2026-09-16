from datetime import date
from pydantic import BaseModel, ConfigDict


class AcademicCalendarResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    calendar_id: int
    academic_year: str
    semester: str
    exam_type: str
    start_date: date
    end_date: date
    is_active: bool

class AcademicCalendarCreate(BaseModel):
    academic_year: str
    semester: str
    exam_type: str
    start_date: date
    end_date: date
    is_active: bool

class AcademicCalendarUpdate(BaseModel):
    academic_year: str | None = None
    semester: str | None = None
    exam_type: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None
