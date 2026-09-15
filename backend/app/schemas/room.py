from pydantic import BaseModel, ConfigDict


class RoomResponse(BaseModel):
    room_code: str
    building: str
    floor: int
    capacity: int

    model_config = ConfigDict(from_attributes=True)


class RoomCreate(BaseModel):
    room_code: str
    building: str
    floor: int
    capacity: int


class RoomUpdate(BaseModel):
    building: str | None = None
    floor: int | None = None
    capacity: int | None = None
