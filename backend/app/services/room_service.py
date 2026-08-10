from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.room import Room


class RoomService:
    def get_all_rooms(self, db: Session) -> list[Room]:
        stmt = select(Room)
        return list(db.scalars(stmt).all())
