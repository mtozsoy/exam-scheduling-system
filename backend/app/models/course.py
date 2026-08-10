from sqlalchemy import Unicode
from sqlalchemy.dialects.mssql import NVARCHAR, TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Course(Base):
    """ORM mapping for the existing SQL Server Ders table."""

    __tablename__ = "Ders"

    course_code: Mapped[str] = mapped_column(
        Unicode(20), primary_key=True, name="DersKodu"
    )
    course_name: Mapped[str] = mapped_column(NVARCHAR, name="DersAdi")
    term: Mapped[int] = mapped_column(TINYINT, name="Donem")
    semester: Mapped[int] = mapped_column(TINYINT, name="Yariyil")