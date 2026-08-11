from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exam_room import ExamRoom
from app.models.room import Room


class ExamRoomService:
    def get_rooms_for_exam(self, db: Session, exam_id: int) -> list[Room]:
        stmt = (
            select(Room)
            .join(ExamRoom, ExamRoom.room_code == Room.room_code)
            .where(ExamRoom.exam_id == exam_id)
        )
        return list(db.scalars(stmt).all())
