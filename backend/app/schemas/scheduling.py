from pydantic import BaseModel, ConfigDict
from datetime import date, time
from typing import List, Optional

class SchedulingProposalRequest(BaseModel):
    course_code: str
    duration_minutes: int
    start_date: date
    end_date: date
    daily_start_time: time
    daily_end_time: time

    model_config = ConfigDict(from_attributes=True)

class RoomAssignment(BaseModel):
    room_code: str
    invigilator_id: int

class SchedulingConfirmRequest(BaseModel):
    course_code: str
    exam_type: str
    date: date
    start_time: time
    end_time: Optional[time] = None
    total_students: Optional[int] = None
    duration_minutes: Optional[int] = None
    rooms: List[RoomAssignment]

class SchedulingConfirmResponse(BaseModel):
    success: bool
    message: str
    exam_id: Optional[int] = None
