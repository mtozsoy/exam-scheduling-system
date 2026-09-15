from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.room import RoomResponse, RoomCreate, RoomUpdate
from app.services.room_service import RoomService

router = APIRouter()


@router.get("/rooms", response_model=list[RoomResponse])
def get_rooms(db: Session = Depends(get_db)):  # noqa: B008
    return RoomService().get_all_rooms(db)


@router.post("/rooms", response_model=RoomResponse)
def create_room(room_in: RoomCreate, db: Session = Depends(get_db)):
    return RoomService().create_room(db, room_in)


@router.put("/rooms/{room_code}", response_model=RoomResponse)
def update_room(room_code: str, room_in: RoomUpdate, db: Session = Depends(get_db)):
    return RoomService().update_room(db, room_code, room_in)


@router.delete("/rooms/{room_code}")
def delete_room(room_code: str, db: Session = Depends(get_db)):
    return RoomService().delete_room(db, room_code)
