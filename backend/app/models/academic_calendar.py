import datetime
from sqlalchemy import Integer, String, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base

class AcademicCalendar(Base):
    __tablename__ = "AkademikTakvim"

    calendar_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, name="TakvimID")
    academic_year: Mapped[str] = mapped_column(String(20), name="AkademikYil")
    semester: Mapped[str] = mapped_column(String(20), name="Donem")
    exam_type: Mapped[str] = mapped_column(String(20), name="SinavTuru")
    start_date: Mapped[datetime.date] = mapped_column(Date, name="BaslangicTarihi")
    end_date: Mapped[datetime.date] = mapped_column(Date, name="BitisTarihi")
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, name="AktifMi")
