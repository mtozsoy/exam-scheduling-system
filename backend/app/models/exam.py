import datetime

from sqlalchemy import Date, Integer, SmallInteger, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Exam(Base):
    """ORM mapping for the existing SQL Server Sinav table."""

    __tablename__ = "Sinav"

    exam_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, name="SinavID"
    )
    course_code: Mapped[str] = mapped_column(String(20), name="DersKodu")
    exam_type: Mapped[str] = mapped_column(String(20), name="SinavTuru")
    date: Mapped[datetime.date] = mapped_column(Date, name="Tarih")
    start_time: Mapped[datetime.time] = mapped_column(Time, name="BaslangicSaati")
    duration_minutes: Mapped[int] = mapped_column(SmallInteger, name="SureDakika")
