from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class Invigilator(Base):
    __tablename__ = "Gozetmen"
    
    invigilator_id: Mapped[int] = mapped_column(Integer, primary_key=True, name="GozetmenID")
    first_name: Mapped[str] = mapped_column(String(50), name="Ad")
    last_name: Mapped[str] = mapped_column(String(50), name="Soyad")
