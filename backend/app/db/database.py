import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

# 1. Ortam Değişkenlerini Yükleme
load_dotenv()

# 2. Connection String'i Okuma
# Örnek SQL Server formatı: 
# "mssql+pyodbc://kullanici_adi:sifre@sunucu_adresi/veritabani_adi?driver=ODBC+Driver+17+for+SQL+Server"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("Kritik Hata: .env dosyasında 'DATABASE_URL' bulunamadı! Lütfen geçerli bir SQL Server bağlantı adresi ekleyin.")

# 3. SQLAlchemy Motoru (Engine)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 4. Veritabanı Oturumu (Session) Üreticisi
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Modeller İçin Temel (Base) Sınıf
class Base(DeclarativeBase):
    pass

# 6. Dependency Injection (Bağımlılık Enjeksiyonu) İçin Session Sağlayıcı
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
