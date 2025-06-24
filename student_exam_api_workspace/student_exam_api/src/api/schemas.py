from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


# PUBLIC_INTERFACE
class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type (Bearer)")


# PUBLIC_INTERFACE
class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


# PUBLIC_INTERFACE
class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None


# PUBLIC_INTERFACE
class UserCreate(UserBase):
    password: str
    role: Optional[Literal["student", "admin"]] = "student"
    class_name: Optional[str] = None


# PUBLIC_INTERFACE
class UserLogin(BaseModel):
    username: str
    password: str


# PUBLIC_INTERFACE
class UserOut(UserBase):
    id: int
    role: str
    class_name: Optional[str] = None

    class Config:
        orm_mode = True


# PUBLIC_INTERFACE
class TimetableBase(BaseModel):
    exam_name: str
    class_name: str
    subject: str
    datetime: datetime
    location: Optional[str] = None


# PUBLIC_INTERFACE
class TimetableCreate(TimetableBase):
    pass


# PUBLIC_INTERFACE
class TimetableOut(TimetableBase):
    id: int

    class Config:
        orm_mode = True


# PUBLIC_INTERFACE
class ScoreCardBase(BaseModel):
    subject: str
    exam_name: str
    score: int
    grade: Optional[str] = None
    remarks: Optional[str] = None


# PUBLIC_INTERFACE
class ScoreCardOut(ScoreCardBase):
    id: int

    class Config:
        orm_mode = True


# PUBLIC_INTERFACE
class AnnouncementBase(BaseModel):
    announcement_type: Literal["exam_paper", "pta_meeting"]
    title: str
    description: Optional[str] = None
    for_class: Optional[str] = None
    event_datetime: Optional[datetime] = None
    attachment_url: Optional[str] = None


# PUBLIC_INTERFACE
class AnnouncementCreate(AnnouncementBase):
    pass


# PUBLIC_INTERFACE
class AnnouncementOut(AnnouncementBase):
    id: int
    created_at: datetime
    uploaded_by: Optional[int] = None

    class Config:
        orm_mode = True
