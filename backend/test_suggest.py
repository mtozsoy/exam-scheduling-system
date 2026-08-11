import sys
import os
import json
from datetime import date, time, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.services.scheduling_service import SchedulingService
from app.models.course import Course

def run_test():
    print("Veritabani baglantisi aciliyor...")
    db = SessionLocal()
    try:
        # 1. Gerçek veritabanından dinamik olarak bir ders seç
        first_course = db.query(Course).first()
        if not first_course:
            print("[UYARI] Veritabaninda hic ders (Course) bulunamadi. Lutfen once ders ekleyin.")
            return
            
        course_code = first_course.course_code
        print(f"\nTest icin secilen gercek ders: {course_code}")
        
        # 2. Parametreleri belirle
        duration = 90
        start_date = date.today() + timedelta(days=1)  # Yarın
        end_date = start_date + timedelta(days=1)      # Yarın ve ertesi gün (2 günlük aralık)
        daily_start = time(9, 0)
        daily_end = time(17, 0)
        
        print(f"Arama Kriterleri: Sure={duration}dk, Tarih={start_date} ile {end_date}, Mesai={daily_start}-{daily_end}\n")
        print("Oneri algoritmasi (suggest_exam_time_slots) calistiriliyor...")
        
        # 3. Metodu test et
        suggestions = SchedulingService.suggest_exam_time_slots(
            db=db,
            course_code=course_code,
            duration_minutes=duration,
            start_date=start_date,
            end_date=end_date,
            daily_start_time=daily_start,
            daily_end_time=daily_end
        )
        
        # 4. Sonuçları konsola bas
        print(f"\n[BASARILI] Toplam {len(suggestions)} adet uygun (cakismasiz) zaman dilimi uretildi:")
        print(json.dumps(suggestions, indent=4))
            
    except Exception as e:
        print(f"\n[HATA] Islem sirasinda hata olustu: {e}")
    finally:
        db.close()
        print("\nVeritabani baglantisi guvenle kapatildi.")

if __name__ == "__main__":
    run_test()
