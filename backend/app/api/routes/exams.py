from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.exam import ExamResponse
from app.services.exam_service import ExamService

router = APIRouter()


@router.get("/exams", response_model=list[ExamResponse])
def get_exams(db: Session = Depends(get_db)):  # noqa: B008
    return ExamService().get_all_exams(db)
