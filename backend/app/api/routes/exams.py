from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.exam import ExamResponse, ExamUpdateRequest
from app.schemas.room import RoomResponse
from app.schemas.invigilator import InvigilatorResponse
from app.services.exam_room_service import ExamRoomService
from app.services.exam_service import ExamService
from app.services.exam_invigilator_service import ExamInvigilatorService

router = APIRouter()


@router.get("/exams", response_model=list[ExamResponse])
def get_exams(db: Session = Depends(get_db)):  # noqa: B008
    return ExamService().get_all_exams(db)


@router.put("/exams/{exam_id}", response_model=ExamResponse)
def update_exam(exam_id: int, request: ExamUpdateRequest, db: Session = Depends(get_db)):
    return ExamService().update_exam(db, exam_id, request)


@router.delete("/exams/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    return ExamService().delete_exam(db, exam_id)


@router.get("/exams/{exam_id}/rooms", response_model=list[RoomResponse])
def get_exam_rooms(exam_id: int, db: Session = Depends(get_db)):
    return ExamRoomService().get_rooms_for_exam(db, exam_id)


@router.get("/exams/{exam_id}/invigilators", response_model=list[InvigilatorResponse])
def get_exam_invigilators(exam_id: int, db: Session = Depends(get_db)):
    return ExamInvigilatorService.get_invigilators_for_exam(db, exam_id)


from app.schemas.exam import StudentExamRoomResponse

@router.get("/exams/{exam_id}/distributions", response_model=list[StudentExamRoomResponse])
def get_exam_distributions(exam_id: int, db: Session = Depends(get_db)):
    from app.models.student_exam_room import StudentExamRoom
    from sqlalchemy import select
    
    # 1. Fetch all student-room mappings for the exam
    records = db.execute(
        select(StudentExamRoom).where(StudentExamRoom.exam_id == exam_id)
    ).scalars().all()
    
    # 2. Group by room_code
    distributions_map = {}
    for record in records:
        if record.room_code not in distributions_map:
            distributions_map[record.room_code] = []
        distributions_map[record.room_code].append(record.student_number)
        
    # 3. Format response
    response = []
    for room_code, students in distributions_map.items():
        response.append(StudentExamRoomResponse(
            room_code=room_code,
            students=students
        ))
        
    return response