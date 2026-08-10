from pydantic import BaseModel, ConfigDict


class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_number: int
    first_name: str
    last_name: str
