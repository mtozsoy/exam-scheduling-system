from collections import defaultdict
from datetime import datetime, timedelta, date, time
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exam import Exam
from app.models.student_course import StudentCourse

class SchedulingService:
    @staticmethod
    def detect_student_exam_conflicts(db: Session) -> list[dict]:
        # 1. Tüm sınavları çek ve tarihlerine göre grupla (Aynı tarihteki sınavları karşılaştırmak için)
        exams = db.execute(select(Exam)).scalars().all()
        
        exams_by_date = defaultdict(list)
        for exam in exams:
            exams_by_date[exam.date].append(exam)
            
        # 2. Tüm ders kayıtlarını çek ve hafızada sözlük (dict -> set) olarak tut.
        # Format: { "DersKodu": {OgrenciNo1, OgrenciNo2} }
        enrollments = db.execute(select(StudentCourse)).scalars().all()
        course_students = defaultdict(set)
        for enrollment in enrollments:
            course_students[enrollment.course_code].add(enrollment.student_number)
            
        conflicts = []
        
        # 3. Sadece aynı gün (date) içindeki sınav çiftlerini (kombinasyonları) karşılaştır
        for date, daily_exams in exams_by_date.items():
            n = len(daily_exams)
            for i in range(n):
                for j in range(i + 1, n):
                    exam1 = daily_exams[i]
                    exam2 = daily_exams[j]
                    
                    # Bitiş zamanlarını hesapla: start_time + duration_minutes
                    # SQLAlchemy Time objelerine direkt dakika eklenemediği için datetime.combine kullanıyoruz
                    start1 = datetime.combine(date, exam1.start_time)
                    end1 = start1 + timedelta(minutes=exam1.duration_minutes)
                    
                    start2 = datetime.combine(date, exam2.start_time)
                    end2 = start2 + timedelta(minutes=exam2.duration_minutes)
                    
                    # Saatlerin gerçekten kesişip kesişmediğini kontrol et
                    # Kesişme şartı: 1. sınavın başlangıcı 2.nin bitişinden önce VE 2.nin başlangıcı 1.nin bitişinden önce olmalı
                    if start1 < end2 and start2 < end1:
                        
                        # 4. Kesişen bu iki sınavın derslerini (course_code) alan ortak öğrencileri bul (Kesişim Kümesi)
                        students1 = course_students[exam1.course_code]
                        students2 = course_students[exam2.course_code]
                        common_students = students1.intersection(students2)
                        
                        # 5. Sadece ortak öğrencisi bulunan çakışmaları listeye ekle
                        for student_num in common_students:
                            conflicts.append({
                                "student_number": student_num,
                                "exam_1_id": exam1.exam_id,
                                "exam_2_id": exam2.exam_id,
                                "exam_1_course": exam1.course_code,
                                "exam_2_course": exam2.course_code,
                                "date": date.isoformat()
                            })
                            
        return conflicts

    @staticmethod
    def suggest_exam_time_slots(
        db: Session,
        course_code: str,
        duration_minutes: int,
        start_date: date,
        end_date: date,
        daily_start_time: time,
        daily_end_time: time
    ) -> list[dict]:
        # 1. İlgili dersin öğrencilerini bul
        enrollments = db.execute(select(StudentCourse)).scalars().all()
        course_students_map = defaultdict(set)
        for e in enrollments:
            course_students_map[e.course_code].add(e.student_number)
        
        target_students = course_students_map.get(course_code, set())
        
        # 2. İlgili tarih aralığındaki mevcut sınavları bul
        existing_exams = db.execute(
            select(Exam).where(Exam.date >= start_date).where(Exam.date <= end_date)
        ).scalars().all()
        
        # 3. Ortak öğrencisi olan (bizim için tehlikeli/bloke) sınavları bul
        blocked_slots = defaultdict(list)
        for exam in existing_exams:
            exam_students = course_students_map.get(exam.course_code, set())
            if target_students.intersection(exam_students):
                exam_start_dt = datetime.combine(exam.date, exam.start_time)
                exam_end_dt = exam_start_dt + timedelta(minutes=exam.duration_minutes)
                blocked_slots[exam.date].append((exam_start_dt, exam_end_dt))
                
        # 4. 30 dakikalık periyotlarla olası tüm zaman slotlarını dene
        available_slots = []
        current_date = start_date
        
        while current_date <= end_date:
            current_time = datetime.combine(current_date, daily_start_time)
            end_time_limit = datetime.combine(current_date, daily_end_time)
            
            while current_time + timedelta(minutes=duration_minutes) <= end_time_limit:
                slot_end_time = current_time + timedelta(minutes=duration_minutes)
                is_overlapping = False
                
                # Bu potansiyel saat, bloke edilmiş bir saat ile çakışıyor mu?
                for blocked_start, blocked_end in blocked_slots[current_date]:
                    if current_time < blocked_end and blocked_start < slot_end_time:
                        is_overlapping = True
                        break
                        
                if not is_overlapping:
                    available_slots.append({
                        "date": current_date.isoformat(),
                        "start_time": current_time.time().isoformat(),
                        "end_time": slot_end_time.time().isoformat()
                    })
                    
                # Bir sonraki olası ihtimal için 30 dakika ileri kaydır
                current_time += timedelta(minutes=30)
                
            current_date += timedelta(days=1)
            
        return available_slots
