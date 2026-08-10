from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.course import CourseResponse
from app.services.course_service import CourseService

router = APIRouter()


@router.get("/courses", response_model=list[CourseResponse])
def get_courses(db: Session = Depends(get_db)):  # noqa: B008
    return CourseService().get_all_courses(db)
