from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.room import Room
from app.models.exam_room import ExamRoom
from app.schemas.room import RoomCreate, RoomUpdate


class RoomService:
    def get_all_rooms(self, db: Session) -> list[Room]:
        stmt = select(Room)
        return list(db.scalars(stmt).all())

    def create_room(self, db: Session, room_in: RoomCreate) -> Room:
        existing = db.execute(
            select(Room).where(Room.room_code == room_in.room_code)
        ).scalars().first()
        if existing:
            raise HTTPException(status_code=400, detail="Bu derslik kodu zaten kullanılıyor.")

        new_room = Room(
            room_code=room_in.room_code,
            building=room_in.building,
            floor=room_in.floor,
            capacity=room_in.capacity,
        )
        db.add(new_room)
        db.commit()
        db.refresh(new_room)
        return new_room

    def update_room(self, db: Session, room_code: str, room_in: RoomUpdate) -> Room:
        room = db.execute(select(Room).where(Room.room_code == room_code)).scalars().first()
        if not room:
            raise HTTPException(status_code=404, detail="Derslik bulunamadı.")

        if room_in.building is not None:
            room.building = room_in.building
        if room_in.floor is not None:
            room.floor = room_in.floor
        if room_in.capacity is not None:
            room.capacity = room_in.capacity

        db.commit()
        db.refresh(room)
        return room

    def delete_room(self, db: Session, room_code: str) -> dict:
        room = db.execute(select(Room).where(Room.room_code == room_code)).scalars().first()
        if not room:
            raise HTTPException(status_code=404, detail="Derslik bulunamadı.")

        # Check if used in ExamRoom
        used = db.execute(select(ExamRoom).where(ExamRoom.room_code == room_code)).scalars().first()
        if used:
            raise HTTPException(
                status_code=409, 
                detail="Bu derslik mevcut bir sınavda kullanıldığı için silinemez."
            )

        db.delete(room)
        db.commit()
        return {"success": True, "message": "Derslik başarıyla silindi."}
