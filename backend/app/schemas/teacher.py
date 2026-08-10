from pydantic import BaseModel, ConfigDict


class TeacherResponse(BaseModel):
    teacher_id: int
    first_name: str
    last_name: str
    title: str

    model_config = ConfigDict(from_attributes=True)
