from pydantic import BaseModel, ConfigDict


class RoomResponse(BaseModel):
    room_code: str
    building: str
    floor: int
    capacity: int

    model_config = ConfigDict(from_attributes=True)
