from collections import defaultdict
from datetime import datetime, timedelta
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
