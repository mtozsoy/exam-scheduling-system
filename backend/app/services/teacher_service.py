from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.teacher import Teacher


class TeacherService:
    def get_all_teachers(self, db: Session) -> list[Teacher]:
        stmt = select(Teacher)
        return list(db.scalars(stmt).all())
