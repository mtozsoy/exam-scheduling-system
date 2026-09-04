import datetime

from pydantic import BaseModel, ConfigDict


class ExamResponse(BaseModel):
    exam_id: int
    course_code: str
    exam_type: str
    date: datetime.date
    start_time: datetime.time
    duration_minutes: int

    model_config = ConfigDict(from_attributes=True)


class ExamUpdateRequest(BaseModel):
    exam_type: str
    date: datetime.date
    start_time: datetime.time
    duration_minutes: int


class StudentExamRoomResponse(BaseModel):
    room_code: str
    students: list[int]

