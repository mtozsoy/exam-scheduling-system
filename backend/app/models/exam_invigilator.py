from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class ExamInvigilator(Base):
    __tablename__ = "SinavGozetmen"

    exam_id: Mapped[int] = mapped_column(Integer, primary_key=True, name="SinavID")
    invigilator_id: Mapped[int] = mapped_column(Integer, primary_key=True, name="GozetmenID")
