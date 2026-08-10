from app.models.student import Student
from sqlalchemy import select
from sqlalchemy.orm import Session


class StudentService:
    """Student-related database operations."""

    def get_all_students(self, db: Session) -> list[Student]:
        """Return every student mapped from the existing Ogrenci table."""
        return db.scalars(select(Student)).all()

    def get_student_by_number(
        self, db: Session, student_number: int
    ) -> Student | None:
        """Return one student by number, or None when no student exists."""
        statement = select(Student).where(Student.student_number == student_number)
        return db.scalars(statement).one_or_none()


        
