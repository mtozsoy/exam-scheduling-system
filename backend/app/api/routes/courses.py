from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.course import CourseResponse
from app.schemas.teacher import TeacherResponse
from app.services.course_service import CourseService
from app.services.course_teacher_service import CourseTeacherService

router = APIRouter()


@router.get("/courses", response_model=list[CourseResponse])
def get_courses(db: Session = Depends(get_db)):  # noqa: B008
    return CourseService().get_all_courses(db)


@router.get("/courses/{course_code}/teachers", response_model=list[TeacherResponse])
def get_course_teachers(course_code: str, db: Session = Depends(get_db)):
    return CourseTeacherService().get_teachers_for_course(db, course_code)
