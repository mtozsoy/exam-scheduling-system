import sys
import os
from datetime import date, time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.services.scheduling_service import SchedulingService
from app.models.course import Course
from app.models.room import Room
from app.models.invigilator import Invigilator
from app.models.exam import Exam
from app.models.exam_invigilator import ExamInvigilator
from sqlalchemy import select

def test_workload_distribution():
    print("Veritabani baglantisi aciliyor...")
    db = SessionLocal()
    
    try:
        # Get invigilators
        invigilators = db.execute(select(Invigilator)).scalars().all()
        if len(invigilators) < 2:
            print("Test için en az 2 gözetmen gerekiyor.")
            return

        inv_busy = invigilators[0]
        inv_free = invigilators[1]
        
        print(f"Test Gözetmenleri: {inv_busy.first_name} (Meşgul edilecek) ve {inv_free.first_name} (Boş kalacak)")

        # Gerçek bir ders bul
        real_course = db.execute(select(Course)).scalars().first()
        if not real_course:
            print("Veritabanında ders bulunamadı.")
            return
            
        real_course_code = real_course.course_code

        # Create a fake exam to increase inv_busy's workload
        fake_exam = Exam(
            course_code=real_course_code,
            exam_type="Vize",
            date=date(2025, 1, 1),
            start_time=time(9, 0),
            duration_minutes=60
        )
        db.add(fake_exam)
        db.flush() # get exam_id

        # Assign it to inv_busy 5 times (or just create 5 exams)
        for i in range(5):
            exam = Exam(
                course_code=real_course_code,
                exam_type="Vize",
                date=date(2025, 1, i+1),
                start_time=time(9, 0),
                duration_minutes=60
            )
            db.add(exam)
            db.flush()
            
            ei = ExamInvigilator(
                exam_id=exam.exam_id,
                invigilator_id=inv_busy.invigilator_id
            )
            db.add(ei)

        db.flush()
        
        # Now generate proposal
        # Öğrencisi olan bir ders bul
        from app.models.student_course import StudentCourse
        enrolled = db.execute(select(StudentCourse.course_code)).scalars().first()
        if enrolled:
            real_course_code = enrolled
        else:
            real_course_code = db.execute(select(Course)).scalars().first().course_code
            
        rooms = db.execute(select(Room)).scalars().all()[:1] # Take 1 room
        
        print("\nOneri algoritmasi calistiriliyor...")
        result = SchedulingService.generate_scheduling_proposals(
            db=db,
            course_code=real_course_code,
            duration_minutes=90,
            start_date=date(2026, 8, 28),
            end_date=date(2026, 8, 29),
            daily_start_time=time(9, 0),
            daily_end_time=time(17, 0),
            available_rooms=rooms
        )
        
        if result["success"] and result["proposals"]:
            proposal = result["proposals"][0]
            assigned_inv_id = proposal["rooms"][0]["invigilator_id"]
            
            print(f"Secilen Gözetmen ID: {assigned_inv_id}")
            if assigned_inv_id == inv_free.invigilator_id or assigned_inv_id != inv_busy.invigilator_id:
                print("[BASARILI] Algoritma daha az gorevi olan gözetmeni secti!")
            else:
                print("[BASARISIZ] Algoritma en cok gorevi olan gözetmeni secti.")
        else:
            print("Öneri bulunamadı.")
            
    finally:
        # Geri al (veritabanı kirlenmesin)
        db.rollback()
        db.close()
        print("Veritabanı işlemleri geri alındı (rollback) ve bağlantı kapatıldı.")

if __name__ == "__main__":
    test_workload_distribution()
