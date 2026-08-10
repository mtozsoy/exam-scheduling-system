from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.course import Course


class CourseService:
    """Course-related database operations."""

    def get_all_courses(self, db: Session) -> list[Course]:
        """Return every course mapped from the existing Ders table."""
        return db.scalars(select(Course)).all()
