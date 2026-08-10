from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.student_course import StudentCourse


class StudentCourseService:
    def get_courses_for_student(self, db: Session, student_number: int) -> list[Course]:
        stmt = (
            select(Course)
            .join(StudentCourse, StudentCourse.course_code == Course.course_code)
            .where(StudentCourse.student_number == student_number)
        )
        return list(db.scalars(stmt).all())
