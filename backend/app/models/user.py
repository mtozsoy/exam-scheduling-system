from sqlalchemy import Column, Integer, String, NVARCHAR
from app.db.database import Base

class User(Base):
    __tablename__ = "Kullanici"

    KullaniciID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    KullaniciAdi = Column(NVARCHAR(50), unique=True, index=True, nullable=False)
    SifreHash = Column(String(255), nullable=False)
    Rol = Column(NVARCHAR(20), nullable=False, default="secretary")
