import sys
import os
import json
from datetime import date, time, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.services.scheduling_service import SchedulingService
from app.models.course import Course
from app.models.room import Room

def run_test():
    print("Veritabani baglantisi aciliyor...")
    db = SessionLocal()
    try:
        # 1. Gerçek veritabanından dinamik olarak bir ders seç
        first_course = db.query(Course).first()
        if not first_course:
            print("[UYARI] Veritabaninda hic ders (Course) bulunamadi.")
            return
            
        course_code = first_course.course_code
        print(f"\nTest icin secilen gercek ders: {course_code}")
        
        # 2. Veritabanından birkaç derslik seç (Kapasite testi için tüm derslikleri alalım)
        available_rooms = db.query(Room).all()
        if not available_rooms:
            print("[UYARI] Veritabaninda hic derslik (Room) bulunamadi.")
            return
            
        print(f"Toplam {len(available_rooms)} adet derslik teste dahil edildi.")
        
        # 3. Parametreleri belirle
        duration = 90
        start_date = date.today() + timedelta(days=1)
        end_date = start_date + timedelta(days=1)
        daily_start = time(9, 0)
        daily_end = time(17, 0)
        
        print(f"Arama Kriterleri: Sure={duration}dk, Tarih={start_date} ile {end_date}, Mesai={daily_start}-{daily_end}\n")
        print("MUKEMMEL SINAV PLANI algoritmasi (generate_scheduling_proposals) calistiriliyor...")
        
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
            print(f"\n[BASARILI] {result['message']}")
            print(json.dumps(result["proposals"][:2], indent=4)) # Çok uzun olmasın diye ilk 2 öneriyi basıyoruz
            if len(result["proposals"]) > 2:
                print(f"\n... ve {len(result['proposals']) - 2} adet daha alternatif mevcut.")
        else:
            print(f"\n[BASARISIZ] {result['message']}")
            
    except Exception as e:
        print(f"\n[HATA] Islem sirasinda hata olustu: {e}")
    finally:
        db.close()
        print("\nVeritabani baglantisi guvenle kapatildi.")

if __name__ == "__main__":
    run_test()
