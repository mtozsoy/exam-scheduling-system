import sys
import os
import json

# Importların doğru çalışması için backend dizinini (mevcut dizini) sys.path'e ekliyoruz
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.services.scheduling_service import SchedulingService

def run_test():
    print("Veritabanı bağlantısı açılıyor (SessionLocal)...")
    db = SessionLocal()
    try:
        print("Çakışma tespit algoritması (SchedulingService.detect_student_exam_conflicts) çağrılıyor...")
        
        # Algoritmayı çalıştır
        conflicts = SchedulingService.detect_student_exam_conflicts(db)
        
        # Sonucu yazdır
        print(f"\n[BASARILI] Algoritma hatasiz tamamlandi! Toplam {len(conflicts)} cakisna tespit edildi.")
        
        if conflicts:
            print("\nÇakışma Detayları:")
            print(json.dumps(conflicts, indent=4, ensure_ascii=False))
        else:
            print("\nHiç çakışan öğrenci bulunamadı. (Eğer veritabanı boşsa bu beklenen bir durumdur.)")
            
    except Exception as e:
        print(f"\n[HATA] HATA OLUSTU: {e}")
    finally:
        db.close()
        print("\nVeritabanı bağlantısı güvenle kapatıldı.")

if __name__ == "__main__":
    run_test()
