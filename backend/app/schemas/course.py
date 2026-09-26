from pydantic import BaseModel, ConfigDict
from typing import Literal


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    course_code: str
    course_name: str
    term: int
    semester: int

class CourseCreate(BaseModel):
    course_code: str
    course_name: str
    term: Literal[1, 2]
    semester: int

class CourseUpdate(BaseModel):
    course_name: str | None = None
    term: Literal[1, 2] | None = None
    semester: int | None = None

