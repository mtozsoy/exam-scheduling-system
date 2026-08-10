from app.db.database import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Student(Base):
    """ORM mapping for the existing SQL Server Ogrenci table."""

    __tablename__ = "Ogrenci"

    student_number: Mapped[int] = mapped_column(
        Integer, primary_key=True, name="OgrenciNo"
    )
    first_name: Mapped[str] = mapped_column(String(50), name="Ad")
    last_name: Mapped[str] = mapped_column(String(50), name="Soyad")
