from app.db.database import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class CourseTeacher(Base):
    """ORM mapping for the existing SQL Server DersOgretmen table."""

    __tablename__ = "DersOgretmen"

    course_code: Mapped[str] = mapped_column(
        String(20), primary_key=True, name="DersKodu"
    )
    teacher_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, name="OgretmenID"
    )
