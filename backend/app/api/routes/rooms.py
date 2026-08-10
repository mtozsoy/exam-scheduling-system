from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.room import RoomResponse
from app.services.room_service import RoomService

router = APIRouter()


@router.get("/rooms", response_model=list[RoomResponse])
def get_rooms(db: Session = Depends(get_db)):  # noqa: B008
    return RoomService().get_all_rooms(db)
