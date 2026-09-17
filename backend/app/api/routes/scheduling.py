from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

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
from app.models.room import Room
from app.models.invigilator import Invigilator
from app.models.student_exam_room import StudentExamRoom
from app.models.student_course import StudentCourse
from app.services.scheduling_service import SchedulingService
from app.services.room_service import RoomService

from app.api.deps import get_current_secretary_or_admin
from fastapi import Depends
router = APIRouter(tags=["scheduling"], dependencies=[Depends(get_current_secretary_or_admin)])

@router.post("/scheduling/proposals")
def generate_proposals(
    request: SchedulingProposalRequest, 
    db: Session = Depends(get_db)
):
    # Akademik Takvim kontrolü
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

@router.post("/scheduling/confirm", response_model=SchedulingConfirmResponse)
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
            raise HTTPException(
                status_code=400,
                detail="Sınav süresi (duration_minutes) veya bitiş saati (end_time) belirtilmelidir."
            )
            
    try:
        # Race Condition Önlemi: Seçilen derslikleri ve gözetmenleri FOR UPDATE (Exclusive Lock) ile kilitle
        # Bu işlem SQL Server üzerinde UPDLOCK/ROWLOCK atarak, onay işlemi bitene kadar başka 
        # bir kullanıcının aynı kaynakları okuyup rezerve etmesini (Phantom Read / Concurrent Modification) engeller.
        selected_room_codes = sorted([r.room_code for r in request.rooms])
        if selected_room_codes:
            print(f"[THREAD] Requesting locks for rooms: {selected_room_codes}")
            db.execute(select(Room).where(Room.room_code.in_(selected_room_codes)).with_hint(Room, 'WITH (UPDLOCK, ROWLOCK)')).scalars().all()
            print(f"[THREAD] Acquired locks for rooms: {selected_room_codes}")
            
        selected_invig_ids = sorted([r.invigilator_id for r in request.rooms if r.invigilator_id is not None])
        if selected_invig_ids:
            db.execute(select(Invigilator).where(Invigilator.invigilator_id.in_(selected_invig_ids)).with_hint(Invigilator, 'WITH (UPDLOCK, ROWLOCK)')).scalars().all()
            
        # --- Güvenlik Kontrolleri ---
        rooms_data = [{"room_code": r.room_code, "invigilator_id": r.invigilator_id} for r in request.rooms]
        print(f"[THREAD] Validating schedule for {request.course_code}")
        validation_result = SchedulingService.validate_exam_schedule(
            db=db,
            course_code=request.course_code,
            exam_type=request.exam_type,
            exam_date=request.date,
            start_time=request.start_time,
            duration_minutes=duration,
            rooms_with_invigilators=rooms_data
        )
        print(f"[THREAD] Validation result: {validation_result['valid']}")
        
        if not validation_result["valid"]:
            raise HTTPException(status_code=409, detail=validation_result["message"])

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
        distributions_map = {}
        
        # Sadece seçilen odaların Room objelerini çek
        selected_rooms = db.execute(
            select(Room).where(Room.room_code.in_(selected_room_codes))
        ).scalars().all()
        
        # Dersi alan öğrencilerin doğrulanması ve kapasite kontrolü distribute_students_to_rooms içinde yapılıyor
        dist_result = SchedulingService.distribute_students_to_rooms(
            db=db,
            course_code=request.course_code,
            available_rooms=selected_rooms
        )
        
        if dist_result.get("success"):
            for d in dist_result.get("distributions", []):
                distributions_map[d["room_code"]] = d["students"]
        else:
            db.rollback()
            return SchedulingConfirmResponse(
                success=False,
                message=f"Öğrenci dağıtımı yapılamadı: {dist_result.get('message', 'Kapasite yetersiz.')}"
            )

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
            
            # Öğrenci - Derslik Eşleştirmesi (StudentExamRoom)
            students = distributions_map.get(room_assignment.room_code, [])
            for student_no in students:
                new_student_room = StudentExamRoom(
                    exam_id=exam_id,
                    room_code=room_assignment.room_code,
                    student_number=student_no
                )
                db.add(new_student_room)
            
        # 3. Tüm işlemler başarılıysa tek bir transaction içinde onayla (Commit)
        print(f"[THREAD] Committing transaction for {request.course_code}")
        db.commit()
        print(f"[THREAD] Transaction committed")
        
        return SchedulingConfirmResponse(
            success=True, 
            message="Sınav başarıyla planlandı.",
            exam_id=exam_id
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Sınav kaydedilirken beklenmeyen bir hata oluştu: {str(e)}")
