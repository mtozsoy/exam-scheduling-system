from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exam import Exam


class ExamService:
    def get_all_exams(self, db: Session) -> list[Exam]:
        stmt = select(Exam)
        return list(db.scalars(stmt).all())
