from app.db.database import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class StudentCourse(Base):
    """ORM mapping for the existing SQL Server OgrenciDers table."""

    __tablename__ = "OgrenciDers"

    student_number: Mapped[int] = mapped_column(
        Integer, primary_key=True, name="OgrenciNo"
    )
    course_code: Mapped[str] = mapped_column(
        String(20), primary_key=True, name="DersKodu"
    )
