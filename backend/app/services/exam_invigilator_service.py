from sqlalchemy.orm import Session
from app.models.exam_invigilator import ExamInvigilator
from app.models.invigilator import Invigilator

class ExamInvigilatorService:
    @staticmethod
    def get_invigilators_for_exam(db: Session, exam_id: int) -> list[Invigilator]:
        return (
            db.query(Invigilator)
            .join(ExamInvigilator, Invigilator.invigilator_id == ExamInvigilator.invigilator_id)
            .filter(ExamInvigilator.exam_id == exam_id)
            .all()
        )
