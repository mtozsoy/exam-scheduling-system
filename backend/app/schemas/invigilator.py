from pydantic import BaseModel, ConfigDict

class InvigilatorBase(BaseModel):
    first_name: str
    last_name: str

class InvigilatorResponse(InvigilatorBase):
    invigilator_id: int

    model_config = ConfigDict(from_attributes=True)

class InvigilatorCreate(InvigilatorBase):
    pass

class InvigilatorUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
