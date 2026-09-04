from app.db.database import Base
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class StudentExamRoom(Base):
    """ORM mapping for the SinavDerslikOgrenci table."""

    __tablename__ = "SinavDerslikOgrenci"

    exam_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("Sinav.SinavID"), primary_key=True, name="SinavID"
    )
    room_code: Mapped[str] = mapped_column(
        String(20), ForeignKey("Derslik.DerslikKodu"), primary_key=True, name="DerslikKodu"
    )
    student_number: Mapped[int] = mapped_column(
        Integer, ForeignKey("Ogrenci.OgrenciNo"), primary_key=True, name="OgrenciNo"
    )
