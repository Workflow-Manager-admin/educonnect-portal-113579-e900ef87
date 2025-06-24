import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class UserRole(str, enum.Enum):
    student = "student"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.student, nullable=False)
    full_name = Column(String(150))
    # Optional class_name for students
    class_name = Column(String(50), nullable=True)

    scores = relationship("ScoreCard", back_populates="user")


class Timetable(Base):
    __tablename__ = "timetables"

    id = Column(Integer, primary_key=True, index=True)
    exam_name = Column(String(200), nullable=False)
    class_name = Column(String(50), nullable=False, index=True)
    subject = Column(String(200), nullable=False)
    datetime = Column(DateTime, nullable=False)
    location = Column(String(200))
    uploaded_by = Column(Integer, ForeignKey("users.id"))


class ScoreCard(Base):
    __tablename__ = "score_cards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String(200), nullable=False)
    exam_name = Column(String(200), nullable=False)
    score = Column(Integer)
    grade = Column(String(10), nullable=True)
    remarks = Column(String(200), nullable=True)

    user = relationship("User", back_populates="scores")


class AnnouncementType(str, enum.Enum):
    exam_paper = "exam_paper"
    pta_meeting = "pta_meeting"


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    announcement_type = Column(Enum(AnnouncementType))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    for_class = Column(String(50), nullable=True)
    event_datetime = Column(DateTime, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    attachment_url = Column(String(500), nullable=True)
