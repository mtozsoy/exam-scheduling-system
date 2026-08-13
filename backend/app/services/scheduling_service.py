from collections import defaultdict
from datetime import datetime, timedelta, date, time
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exam import Exam
from app.models.student_course import StudentCourse
from app.models.exam_room import ExamRoom
from app.models.invigilator import Invigilator
from app.models.exam_invigilator import ExamInvigilator
from app.models.room import Room

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
    def validate_exam_schedule(
        db: Session,
        course_code: str,
        exam_date: date,
        start_time: time,
        duration_minutes: int,
        rooms_with_invigilators: list[dict]
    ) -> dict:
        # 1. Aynı course_code için zaten bir sınav kaydı var mı?
        existing_exam = db.execute(
            select(Exam).where(Exam.course_code == course_code)
        ).scalars().first()
        if existing_exam:
            return {"valid": False, "message": f"Bu ders ({course_code}) için zaten planlanmış bir sınav bulunmaktadır."}

        target_start = datetime.combine(exam_date, start_time)
        target_end = target_start + timedelta(minutes=duration_minutes)

        # 2. Seçilen tarih/saatte öğrencilerin başka sınavlarıyla çakışma var mı?
        enrollments = db.execute(select(StudentCourse)).scalars().all()
        course_students_map = defaultdict(set)
        for e in enrollments:
            course_students_map[e.course_code].add(e.student_number)
            
        target_students = course_students_map.get(course_code, set())
        
        daily_exams = db.execute(
            select(Exam).where(Exam.date == exam_date)
        ).scalars().all()
        
        for exam in daily_exams:
            if exam.course_code == course_code:
                continue
                
            ex_start = datetime.combine(exam.date, exam.start_time)
            ex_end = ex_start + timedelta(minutes=exam.duration_minutes)
            
            # Zaman kesişimi var mı?
            if target_start < ex_end and ex_start < target_end:
                exam_students = course_students_map.get(exam.course_code, set())
                if target_students.intersection(exam_students):
                    return {"valid": False, "message": f"Öğrenci çakışması tespit edildi. ({exam.course_code} sınavı ile ortak öğrenciler var)."}

        # 3. Seçilen dersliklerden herhangi biri aynı zaman aralığında başka sınavda kullanılıyor mu?
        requested_room_codes = [r["room_code"] for r in rooms_with_invigilators]
        if requested_room_codes:
            exam_rooms = db.execute(
                select(ExamRoom, Exam)
                .join(Exam, ExamRoom.exam_id == Exam.exam_id)
                .where(Exam.date == exam_date)
                .where(ExamRoom.room_code.in_(requested_room_codes))
            ).all()
            
            for er, exam in exam_rooms:
                if exam.course_code == course_code:
                    continue
                ex_start = datetime.combine(exam.date, exam.start_time)
                ex_end = ex_start + timedelta(minutes=exam.duration_minutes)
                if target_start < ex_end and ex_start < target_end:
                    return {"valid": False, "message": f"Derslik çakışması! {er.room_code} numaralı derslik bu saatlerde başka bir sınava ({exam.course_code}) tahsis edilmiş."}

        # 4. Atanan gözetmenlerden herhangi biri aynı zaman aralığında başka sınavda görevli mi?
        requested_invigilator_ids = [r["invigilator_id"] for r in rooms_with_invigilators]
        if requested_invigilator_ids:
            exam_invigilators = db.execute(
                select(ExamInvigilator, Exam)
                .join(Exam, ExamInvigilator.exam_id == Exam.exam_id)
                .where(Exam.date == exam_date)
                .where(ExamInvigilator.invigilator_id.in_(requested_invigilator_ids))
            ).all()
            
            for ei, exam in exam_invigilators:
                if exam.course_code == course_code:
                    continue
                ex_start = datetime.combine(exam.date, exam.start_time)
                ex_end = ex_start + timedelta(minutes=exam.duration_minutes)
                if target_start < ex_end and ex_start < target_end:
                    return {"valid": False, "message": f"Gözetmen çakışması! ID'si {ei.invigilator_id} olan gözetmen bu saatlerde başka bir sınavda ({exam.course_code}) görevli."}

        # 5. Kullanılan dersliklerin toplam kapasitesi sınava girecek öğrenci sayısını karşılıyor mu?
        total_students = len(target_students)
        total_capacity = 0
        if requested_room_codes:
            rooms_info = db.execute(
                select(Room).where(Room.room_code.in_(requested_room_codes))
            ).scalars().all()
            total_capacity = sum(r.capacity for r in rooms_info)
            
        if total_students > total_capacity:
            return {"valid": False, "message": f"Kapasite yetersiz! Sınava girecek öğrenci sayısı ({total_students}), seçilen dersliklerin toplam kapasitesini ({total_capacity}) aşıyor."}

        return {"valid": True, "message": "Tüm güvenlik kontrolleri başarılı."}

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

    @staticmethod
    def distribute_students_to_rooms(
        db: Session,
        course_code: str,
        available_rooms: list
    ) -> dict:
        # 1. İlgili dersi alan öğrencilerin numaralarını bul
        enrollments = db.execute(
            select(StudentCourse.student_number).where(StudentCourse.course_code == course_code)
        ).scalars().all()
        
        students = list(enrollments)
        total_students = len(students)
        
        # 2. Seçilen dersliklerin (available_rooms) toplam kapasitesini hesapla
        total_capacity = sum(room.capacity for room in available_rooms)
        
        # 3. Kapasite yeterliliğini kontrol et
        if total_students > total_capacity:
            return {
                "success": False,
                "message": "Toplam kapasite yetersiz!",
                "total_students": total_students,
                "total_capacity": total_capacity,
                "missing_capacity": total_students - total_capacity,
                "distributions": []
            }
            
        # 4. Öğrencileri kapasiteyi aşmadan dersliklere (odaklara) bölüştür
        distributions = []
        student_idx = 0
        
        for room in available_rooms:
            # Eğer dağıtılacak öğrenci kalmadıysa boşuna diğer derslikleri gezme
            if student_idx >= total_students:
                break
                
            # Dersliğin kapasitesi kadar öğrenci al (Slice)
            assigned_students = students[student_idx : student_idx + room.capacity]
            
            distributions.append({
                "room_code": room.room_code,
                "capacity": room.capacity,
                "assigned_count": len(assigned_students),
                "students": assigned_students
            })
            
            # Index'i atadığımız kişi sayısı kadar ileri kaydır
            student_idx += room.capacity
            
        # Sonucu frontend'in çok rahat kullanabileceği bir JSON yapısıyla dönüyoruz
        return {
            "success": True,
            "message": "Öğrenciler dersliklere başarıyla yerleştirildi.",
            "total_students": total_students,
            "total_capacity": total_capacity,
            "distributions": distributions
        }

    @staticmethod
    def generate_scheduling_proposals(
        db: Session,
        course_code: str,
        duration_minutes: int,
        start_date: date,
        end_date: date,
        daily_start_time: time,
        daily_end_time: time,
        available_rooms: list
    ) -> dict:
        
        # 1. Önce öğrenci çakışması yaratmayan güvenli zaman dilimlerini (slotları) hesapla
        available_slots = SchedulingService.suggest_exam_time_slots(
            db=db,
            course_code=course_code,
            duration_minutes=duration_minutes,
            start_date=start_date,
            end_date=end_date,
            daily_start_time=daily_start_time,
            daily_end_time=daily_end_time
        )
        
        if not available_slots:
            return {
                "success": False,
                "message": "Planlama Başarısız: Öğrenci çakışması yaratmayacak hiçbir uygun boş zaman bulunamadı.",
                "proposals": []
            }
            
        # 2. Mevcut sınav saatlerini ve kullanılan derslikleri çek
        existing_exams = db.execute(
            select(Exam).where(Exam.date >= start_date).where(Exam.date <= end_date)
        ).scalars().all()
        
        exam_times = {}
        for ex in existing_exams:
            ex_start = datetime.combine(ex.date, ex.start_time)
            ex_end = ex_start + timedelta(minutes=ex.duration_minutes)
            exam_times[ex.exam_id] = (ex_start, ex_end)
            
        exam_rooms = db.execute(select(ExamRoom)).scalars().all()
        room_busy_slots = defaultdict(list)
        for er in exam_rooms:
            if er.exam_id in exam_times:
                room_busy_slots[er.room_code].append(exam_times[er.exam_id])

        # Mevcut gözetmenlerin meşguliyetlerini çek
        exam_invigilators = db.execute(select(ExamInvigilator)).scalars().all()
        invigilator_busy_slots = defaultdict(list)
        for ei in exam_invigilators:
            if ei.exam_id in exam_times:
                invigilator_busy_slots[ei.invigilator_id].append(exam_times[ei.exam_id])
                
        # Sistemdeki tüm gözetmenleri al (Müsaitlik kontrolü için)
        all_invigilators = db.execute(select(Invigilator)).scalars().all()

        # 3. Her bir güvenli zaman dilimi için derslik kapasitelerini dinamik olarak test et
        proposals = []
        for slot in available_slots:
            slot_start = datetime.fromisoformat(f"{slot['date']}T{slot['start_time']}")
            slot_end = datetime.fromisoformat(f"{slot['date']}T{slot['end_time']}")
            
            # Bu saatte dolu olmayan (tamamen müsait) derslikleri filtrele
            free_rooms = []
            for room in available_rooms:
                is_room_busy = False
                for busy_start, busy_end in room_busy_slots[room.room_code]:
                    # Çakışma kontrolü (Saatlerin kesişmesi)
                    if slot_start < busy_end and busy_start < slot_end:
                        is_room_busy = True
                        break
                
                if not is_room_busy:
                    free_rooms.append(room)
            
            # Sadece bu saatte boş olan dersliklerle kapasite testi ve öğrenci dağılımı yap
            distribution_result = SchedulingService.distribute_students_to_rooms(
                db=db, 
                course_code=course_code, 
                available_rooms=free_rooms
            )
            
            # Eğer derslik kapasitesi yeterliyse Gözetmen kontrolüne geç
            if distribution_result.get("success"):
                distributions = distribution_result["distributions"]
                needed_invigilator_count = len(distributions)
                
                # Bu saatte müsait olan gözetmenleri filtrele
                free_invigilators = []
                for inv in all_invigilators:
                    is_inv_busy = False
                    for busy_start, busy_end in invigilator_busy_slots[inv.invigilator_id]:
                        if slot_start < busy_end and busy_start < slot_end:
                            is_inv_busy = True
                            break
                    
                    if not is_inv_busy:
                        free_invigilators.append(inv)
                        
                # Eğer yeterli sayıda müsait gözetmen varsa öneriyi kaydet
                if len(free_invigilators) >= needed_invigilator_count:
                    assigned_invigilators = free_invigilators[:needed_invigilator_count]
                    
                    # Her dersliğe bir gözetmen ata
                    for i, dist in enumerate(distributions):
                        dist["invigilator_id"] = assigned_invigilators[i].invigilator_id
                        
                    proposals.append({
                        "date": slot["date"],
                        "start_time": slot["start_time"],
                        "end_time": slot["end_time"],
                        "total_students": distribution_result["total_students"],
                        "rooms": distributions
                    })
                
        if not proposals:
            return {
                "success": False,
                "message": "Öğrenci çakışması olmayan zamanlar bulundu ancak o saatlerde boş derslik veya yeterli sayıda müsait gözetmen bulunamadı.",
                "proposals": []
            }
            
        return {
            "success": True,
            "message": f"Toplam {len(proposals)} adet (öğrenci ve derslik çakışması olmayan) güvenli sınav planı önerisi başarıyla oluşturuldu.",
            "proposals": proposals
        }
