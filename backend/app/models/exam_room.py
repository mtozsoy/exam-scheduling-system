from app.db.database import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class ExamRoom(Base):
    """ORM mapping for the existing SQL Server SinavDerslik table."""

    __tablename__ = "SinavDerslik"

    exam_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, name="SinavID"
    )
    room_code: Mapped[str] = mapped_column(
        String(20), primary_key=True, name="DerslikKodu"
    )
