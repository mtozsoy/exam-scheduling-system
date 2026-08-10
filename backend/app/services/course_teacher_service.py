from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.course_teacher import CourseTeacher
from app.models.teacher import Teacher


class CourseTeacherService:
    def get_teachers_for_course(self, db: Session, course_code: str) -> list[Teacher]:
        stmt = (
            select(Teacher)
            .join(CourseTeacher, CourseTeacher.teacher_id == Teacher.teacher_id)
            .where(CourseTeacher.course_code == course_code)
        )
        return list(db.scalars(stmt).all())
