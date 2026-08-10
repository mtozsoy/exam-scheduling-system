from app.db.database import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Teacher(Base):
    """ORM mapping for the existing SQL Server Ogretmen table."""

    __tablename__ = "Ogretmen"

    teacher_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, name="OgretmenID"
    )
    first_name: Mapped[str] = mapped_column(String(50), name="Ad")
    last_name: Mapped[str] = mapped_column(String(50), name="Soyad")
    title: Mapped[str] = mapped_column(String(50), name="Unvan")
