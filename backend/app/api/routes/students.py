from app.db.database import get_db
from app.schemas.course import CourseResponse
from app.schemas.student import StudentResponse
from app.services.student_course_service import StudentCourseService
from app.services.student_service import StudentService
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/students", response_model=list[StudentResponse])
def get_students(db: Session = Depends(get_db)):  # noqa: B008
    return StudentService().get_all_students(db)


@router.get("/students/{student_number}", response_model=StudentResponse)
def get_student(student_number: int, db: Session = Depends(get_db)):
    student = StudentService().get_student_by_number(db, student_number)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.get("/students/{student_number}/courses", response_model=list[CourseResponse])
def get_student_courses(student_number: int, db: Session = Depends(get_db)):
    return StudentCourseService().get_courses_for_student(db, student_number)
