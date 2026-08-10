from sqlalchemy import SmallInteger, String
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Room(Base):
    """ORM mapping for the existing SQL Server Derslik table."""

    __tablename__ = "Derslik"

    room_code: Mapped[str] = mapped_column(
        String(20), primary_key=True, name="DerslikKodu"
    )
    building: Mapped[str] = mapped_column(String(50), name="Bina")
    floor: Mapped[int] = mapped_column(TINYINT, name="Kat")
    capacity: Mapped[int] = mapped_column(SmallInteger, name="Kapasite")
