from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exam import Exam
from app.models.exam_room import ExamRoom
from app.models.exam_invigilator import ExamInvigilator
from app.schemas.exam import ExamUpdateRequest
from app.services.scheduling_service import SchedulingService

class ExamService:
    def get_all_exams(self, db: Session) -> list[Exam]:
        stmt = select(Exam)
        return list(db.scalars(stmt).all())

    def update_exam(self, db: Session, exam_id: int, request: ExamUpdateRequest) -> Exam:
        # 1. Sınavı bul
        exam = db.execute(select(Exam).where(Exam.exam_id == exam_id)).scalars().first()
        if not exam:
            raise HTTPException(status_code=404, detail="Sınav bulunamadı.")
            
        # 2. Mevcut odaları ve gözetmenleri formatla
        exam_rooms = db.execute(select(ExamRoom).where(ExamRoom.exam_id == exam_id)).scalars().all()
        # Bir sınavda gözetmenler odaya özel atanmış olabilir, burada basitçe eşliyoruz. 
        # (Gerçek sistemde her ExamRoom'un karşılığı olan Invigilator'u çekmek daha sağlıklı ama list[dict] istiyor validate)
        exam_invigs = db.execute(select(ExamInvigilator).where(ExamInvigilator.exam_id == exam_id)).scalars().all()
        
        # SchedulingService'in beklentisi: list[dict] {"room_code": "...", "invigilator_id": ...}
        # Oda sayısı ve gözetmen sayısı eşit olmayabilir. Hiçbir veriyi kaybetmemek için zip_longest kullanıyoruz.
        from itertools import zip_longest
        rooms_with_invigilators = []
        for room, invig in zip_longest(exam_rooms, exam_invigs):
            rooms_with_invigilators.append({
                "room_code": room.room_code if room else None,
                "invigilator_id": invig.invigilator_id if invig else None
            })

        # 3. Validation yap (kendi exam_id'mizi hariç tutarak)
        val_result = SchedulingService.validate_exam_schedule(
            db=db,
            course_code=exam.course_code,
            exam_type=request.exam_type,
            exam_date=request.date,
            start_time=request.start_time,
            duration_minutes=request.duration_minutes,
            rooms_with_invigilators=rooms_with_invigilators,
            exclude_exam_id=exam_id
        )
        
        if not val_result["valid"]:
            raise HTTPException(status_code=409, detail=val_result["message"])
            
        # 4. Sınavı güncelle
        exam.exam_type = request.exam_type
        exam.date = request.date
        exam.start_time = request.start_time
        exam.duration_minutes = request.duration_minutes
        
        try:
            db.commit()
            db.refresh(exam)
        except Exception:
            db.rollback()
            raise
            
        return exam

    def delete_exam(self, db: Session, exam_id: int):
        from sqlalchemy import delete
        
        # 1. Sınavı bul
        exam = db.execute(select(Exam).where(Exam.exam_id == exam_id)).scalars().first()
        if not exam:
            raise HTTPException(status_code=404, detail="Sınav bulunamadı.")
            
        try:
            # Bağımlı kayıtları temizle (Eğer veritabanında ON DELETE CASCADE yoksa manuel silmek güvenlidir)
            from app.models.student_exam_room import StudentExamRoom
            db.execute(delete(StudentExamRoom).where(StudentExamRoom.exam_id == exam_id))
            db.execute(delete(ExamRoom).where(ExamRoom.exam_id == exam_id))
            db.execute(delete(ExamInvigilator).where(ExamInvigilator.exam_id == exam_id))
            # Sınavı sil
            db.execute(delete(Exam).where(Exam.exam_id == exam_id))
            db.commit()
        except Exception:
            db.rollback()
            raise
            
        return {"success": True, "message": "Sınav başarıyla silindi."}
