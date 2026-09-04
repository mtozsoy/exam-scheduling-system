import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db.database import engine

def create_table():
    with engine.begin() as conn:
        conn.execute(text("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='SinavDerslikOgrenci' and xtype='U')
        CREATE TABLE SinavDerslikOgrenci (
            SinavID int NOT NULL,
            DerslikKodu nvarchar(20) NOT NULL,
            OgrenciNo int NOT NULL,
            CONSTRAINT PK_SinavDerslikOgrenci PRIMARY KEY (SinavID, DerslikKodu, OgrenciNo),
            CONSTRAINT FK_SinavDerslikOgrenci_Sinav FOREIGN KEY (SinavID) REFERENCES Sinav(SinavID) ON DELETE CASCADE,
            CONSTRAINT FK_SinavDerslikOgrenci_Derslik FOREIGN KEY (DerslikKodu) REFERENCES Derslik(DerslikKodu) ON DELETE CASCADE,
            CONSTRAINT FK_SinavDerslikOgrenci_Ogrenci FOREIGN KEY (OgrenciNo) REFERENCES Ogrenci(OgrenciNo) ON DELETE CASCADE
        )
        """))
        print("Tablo oluşturuldu (veya zaten var).")

if __name__ == "__main__":
    create_table()
