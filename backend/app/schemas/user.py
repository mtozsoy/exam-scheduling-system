from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., alias="KullaniciAdi")
    role: str = Field(..., alias="Rol")

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, alias="KullaniciAdi")
    role: Optional[str] = Field(None, alias="Rol")
    password: Optional[str] = None

class UserOut(UserBase):
    id: int = Field(..., alias="KullaniciID")

    class Config:
        from_attributes = True
        populate_by_name = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str
