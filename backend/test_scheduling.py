import sys
import os
import json
from datetime import date, time, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.services.scheduling_service import SchedulingService
from app.models.course import Course
from app.models.room import Room
from app.models.student_course import StudentCourse

def run_test():
    print("Veritabani baglantisi aciliyor...")
    db = SessionLocal()
    try:
        # 1. İçinde (varsa) öğrenci olan bir ders bulmaya çalış
        enrolled_course = db.query(StudentCourse.course_code).first()
        
        if enrolled_course:
            course_code = enrolled_course.course_code
            print(f"\n[BILGI] Test icin ogrencisi olan gercek ders secildi: {course_code}")
        else:
            first_course = db.query(Course).first()
            if not first_course:
                print("[UYARI] Veritabaninda hic ders (Course) bulunamadi.")
                return
            course_code = first_course.course_code
            print(f"\n[BILGI] Veritabaninda hic ders kaydi/ogrenci eslesmesi bulunamadi. Rastgele secilen ders: {course_code}")
        
        # 2. Veritabanından derslikleri seç
        available_rooms = db.query(Room).all()
        if not available_rooms:
            print("[UYARI] Veritabaninda hic derslik (Room) bulunamadi.")
            return
            
        print(f"Toplam {len(available_rooms)} adet derslik teste dahil edildi.")
        
        # 3. Parametreleri belirle
        duration = 90
        start_date = date.today() + timedelta(days=1)
        end_date = start_date + timedelta(days=2) # 3 günlük aralık
        daily_start = time(9, 0)
        daily_end = time(17, 0)
        
        print(f"Arama Kriterleri: Sure={duration}dk, Tarih={start_date} - {end_date}, Mesai={daily_start}-{daily_end}\n")
        print("Sınav planlama algoritmasi calistiriliyor...")
        
        # 4. Ana metodu test et
        result = SchedulingService.generate_scheduling_proposals(
            db=db,
            course_code=course_code,
            duration_minutes=duration,
            start_date=start_date,
            end_date=end_date,
            daily_start_time=daily_start,
            daily_end_time=daily_end,
            available_rooms=available_rooms
        )
        
        # 5. Sonuçları konsola bas
        if result["success"]:
            proposals = result["proposals"]
            print(f"\n[BASARILI] Toplam {len(proposals)} adet plan olusturuldu.")
            
            # Sadece ilk 3 tanesini göster
            sample = proposals[:3]
            print("\n--- ILK 3 ONERI DETAYI ---")
            print(json.dumps(sample, indent=4))
        else:
            print(f"\n[BASARISIZ] {result['message']}")
            
    except Exception as e:
        print(f"\n[HATA] Islem sirasinda hata olustu: {e}")
    finally:
        db.close()
        print("\nVeritabani baglantisi kapatildi.")

if __name__ == "__main__":
    run_test()
