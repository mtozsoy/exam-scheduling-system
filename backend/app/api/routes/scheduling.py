from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.scheduling import (
    SchedulingProposalRequest,
    SchedulingConfirmRequest,
    SchedulingConfirmResponse
)
from app.models.exam import Exam
from app.models.exam_room import ExamRoom
from app.models.exam_invigilator import ExamInvigilator
from app.models.academic_calendar import AcademicCalendar
from app.services.scheduling_service import SchedulingService
from app.services.room_service import RoomService

router = APIRouter(prefix="/scheduling", tags=["scheduling"])

@router.post("/proposals")
def generate_proposals(
    request: SchedulingProposalRequest, 
    db: Session = Depends(get_db)
):
    # Akademik Takvim kontrolü
    from sqlalchemy import select
    active_calendar = db.execute(
        select(AcademicCalendar).where(
            AcademicCalendar.is_active == True,
            AcademicCalendar.exam_type == request.exam_type
        )
    ).scalars().first()

    if not active_calendar:
        raise HTTPException(
            status_code=404,
            detail=f"Aktif bir akademik takvim bulunamadı. Lütfen '{request.exam_type}' sınav türü için aktif bir takvim tanımlayın."
        )

    room_service = RoomService()
    # Mevcut tüm derslikleri veritabanından çek (veya request'ten seçili olanları alabilirdik, şimdilik tümünü alıyoruz)
    available_rooms = room_service.get_all_rooms(db)
    
    result = SchedulingService.generate_scheduling_proposals(
        db=db,
        course_code=request.course_code,
        duration_minutes=request.duration_minutes,
        start_date=active_calendar.start_date,
        end_date=active_calendar.end_date,
        daily_start_time=request.daily_start_time,
        daily_end_time=request.daily_end_time,
        available_rooms=available_rooms
    )
    
    return result

@router.post("/confirm", response_model=SchedulingConfirmResponse)
def confirm_proposal(
    request: SchedulingConfirmRequest,
    db: Session = Depends(get_db)
):
    # duration_minutes gönderilmemişse (proposal kopyalanmışsa) start_time ve end_time üzerinden hesapla
    duration = request.duration_minutes
    if duration is None:
        if request.end_time:
            import datetime
            start_dt = datetime.datetime.combine(request.date, request.start_time)
            end_dt = datetime.datetime.combine(request.date, request.end_time)
            duration = int((end_dt - start_dt).total_seconds() / 60)
        else:
            duration = 90 # Fallback

    # --- Güvenlik Kontrolleri ---
    rooms_data = [{"room_code": r.room_code, "invigilator_id": r.invigilator_id} for r in request.rooms]
    validation_result = SchedulingService.validate_exam_schedule(
        db=db,
        course_code=request.course_code,
        exam_type=request.exam_type,
        exam_date=request.date,
        start_time=request.start_time,
        duration_minutes=duration,
        rooms_with_invigilators=rooms_data
    )
    
    if not validation_result["valid"]:
        raise HTTPException(status_code=409, detail=validation_result["message"])

    try:
        # 1. Ana Sınav (Exam) kaydını oluştur
        new_exam = Exam(
            course_code=request.course_code,
            exam_type=request.exam_type,
            date=request.date,
            start_time=request.start_time,
            duration_minutes=duration
        )
        db.add(new_exam)
        db.flush() # Veritabanından otomatik oluşan exam_id'yi almak için
        
        exam_id = new_exam.exam_id
        
        # 2. Derslik ve Gözetmen atamalarını ilgili tablolara (ExamRoom ve ExamInvigilator) kaydet
        for room_assignment in request.rooms:
            # Derslik (ExamRoom)
            new_room = ExamRoom(
                exam_id=exam_id,
                room_code=room_assignment.room_code
            )
            db.add(new_room)
            
            # Gözetmen (ExamInvigilator)
            new_invigilator = ExamInvigilator(
                exam_id=exam_id,
                invigilator_id=room_assignment.invigilator_id
            )
            db.add(new_invigilator)
            
        # 3. Tüm işlemler başarılıysa tek bir transaction içinde onayla (Commit)
        db.commit()
        
        return SchedulingConfirmResponse(
            success=True,
            message="Sınav başarıyla planlandı ve veritabanına kaydedildi.",
            exam_id=exam_id
        )
        
    except Exception as e:
        # Hata durumunda hiçbir kaydı bırakma, geri al (Rollback)
        db.rollback()
        return SchedulingConfirmResponse(
            success=False,
            message=f"Kayıt sırasında bir hata oluştu. İşlem iptal edildi: {str(e)}"
        )
