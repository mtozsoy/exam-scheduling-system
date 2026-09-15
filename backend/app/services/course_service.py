from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.course import Course
from app.models.student_course import StudentCourse
from app.models.course_teacher import CourseTeacher
from app.models.exam import Exam
from app.schemas.course import CourseCreate, CourseUpdate

class CourseService:
    """Course-related database operations."""

    def get_all_courses(self, db: Session) -> list[Course]:
        """Return every course mapped from the existing Ders table."""
        return list(db.scalars(select(Course)).all())

    def create_course(self, db: Session, course_in: CourseCreate) -> Course:
        # Check if course_code already exists
        existing = db.execute(select(Course).where(Course.course_code == course_in.course_code)).scalars().first()
        if existing:
            raise HTTPException(status_code=409, detail="Bu ders kodu ile zaten bir kayıt bulunmaktadır.")

        new_course = Course(
            course_code=course_in.course_code,
            course_name=course_in.course_name,
            term=course_in.term,
            semester=course_in.semester
        )
        db.add(new_course)
        db.commit()
        db.refresh(new_course)
        return new_course

    def update_course(self, db: Session, course_code: str, course_in: CourseUpdate) -> Course:
        course = db.execute(select(Course).where(Course.course_code == course_code)).scalars().first()
        if not course:
            raise HTTPException(status_code=404, detail="Ders bulunamadı.")

        if course_in.course_name is not None:
            course.course_name = course_in.course_name
        if course_in.term is not None:
            course.term = course_in.term
        if course_in.semester is not None:
            course.semester = course_in.semester

        db.commit()
        db.refresh(course)
        return course

    def delete_course(self, db: Session, course_code: str) -> dict:
        course = db.execute(select(Course).where(Course.course_code == course_code)).scalars().first()
        if not course:
            raise HTTPException(status_code=404, detail="Ders bulunamadı.")

        # Integrity Check 1: Students
        has_students = db.execute(select(StudentCourse).where(StudentCourse.course_code == course_code)).scalars().first()
        if has_students:
            raise HTTPException(status_code=409, detail="Bu derse kayıtlı öğrenci bulunduğu için ders silinemez.")

        # Integrity Check 2: Teachers
        has_teachers = db.execute(select(CourseTeacher).where(CourseTeacher.course_code == course_code)).scalars().first()
        if has_teachers:
            raise HTTPException(status_code=409, detail="Bu derse atanmış öğretmen bulunduğu için ders silinemez.")

        # Integrity Check 3: Exams
        has_exams = db.execute(select(Exam).where(Exam.course_code == course_code)).scalars().first()
        if has_exams:
            raise HTTPException(status_code=409, detail="Bu dersin planlanmış bir sınavı bulunduğu için ders silinemez.")

        db.delete(course)
        db.commit()
        return {"success": True, "message": "Ders başarıyla silindi."}
