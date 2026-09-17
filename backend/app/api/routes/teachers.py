from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.teacher import TeacherResponse
from app.services.teacher_service import TeacherService

from app.api.deps import get_current_secretary_or_admin
from fastapi import Depends
router = APIRouter(dependencies=[Depends(get_current_secretary_or_admin)])


@router.get("/teachers", response_model=list[TeacherResponse])
def get_teachers(db: Session = Depends(get_db)):  # noqa: B008
    return TeacherService().get_all_teachers(db)
