import io
import csv
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from . import models, schemas, auth

router = APIRouter()


# --- AUTH ---


@router.post(
    "/auth/login",
    response_model=schemas.Token,
    summary="Login as student or admin",
    tags=["Auth"],
)
def login(form: schemas.UserLogin, db: Session = Depends(auth.get_db)):
    user = auth.authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


# --- USERS ---


@router.post(
    "/auth/register",
    response_model=schemas.UserOut,
    summary="Register a new user (admin only)",
    tags=["Users"],
)
def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(auth.get_db),
    admin: models.User = Depends(auth.get_current_admin),
):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(409, "Username already exists")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        role=user.role,
        full_name=user.full_name,
        class_name=user.class_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get(
    "/users/me",
    response_model=schemas.UserOut,
    summary="Get details of the current user",
    tags=["Users"],
)
def get_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user


# --- TIMETABLE ---


@router.get(
    "/timetable",
    response_model=List[schemas.TimetableOut],
    summary="List timetable entries (student)",
    tags=["Timetable"],
)
def list_timetable(
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    query = db.query(models.Timetable)
    if (
        current_user.role == models.UserRole.student
        and current_user.class_name
    ):
        query = query.filter(models.Timetable.class_name == current_user.class_name)
    return query.order_by(models.Timetable.datetime.asc()).all()


@router.get(
    "/timetable/search",
    response_model=List[schemas.TimetableOut],
    summary="Search timetable by class",
    tags=["Timetable"],
)
def search_timetable(class_name: str, db: Session = Depends(auth.get_db)):
    return (
        db.query(models.Timetable)
        .filter(models.Timetable.class_name == class_name)
        .order_by(models.Timetable.datetime.asc())
        .all()
    )


@router.post(
    "/timetable",
    response_model=schemas.TimetableOut,
    summary="Admin can upload timetable entry",
    tags=["Timetable"],
)
def create_timetable(
    timetable: schemas.TimetableCreate,
    db: Session = Depends(auth.get_db),
    admin: models.User = Depends(auth.get_current_admin),
):
    db_tt = models.Timetable(**timetable.dict(), uploaded_by=admin.id)
    db.add(db_tt)
    db.commit()
    db.refresh(db_tt)
    return db_tt


@router.get(
    "/timetable/download",
    summary="Download timetable as CSV for a class",
    tags=["Timetable"],
)
def download_timetable(class_name: str, db: Session = Depends(auth.get_db)):
    items = (
        db.query(models.Timetable)
        .filter(models.Timetable.class_name == class_name)
        .order_by(models.Timetable.datetime.asc())
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Exam Name", "Class", "Subject", "Datetime", "Location"])
    for tt in items:
        writer.writerow(
            [tt.exam_name, tt.class_name, tt.subject, tt.datetime, tt.location]
        )
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                f"attachment; filename=timetable_{class_name}.csv"
            )
        },
    )


# --- SCORE CARD ---


@router.get(
    "/scores",
    response_model=List[schemas.ScoreCardOut],
    summary="View my score card",
    tags=["Score Card"],
)
def get_my_scores(
    db: Session = Depends(auth.get_db),
    user: models.User = Depends(auth.get_current_active_user),
):
    # Only student can view own scores, admin must query by user id
    if user.role == models.UserRole.student:
        query = db.query(models.ScoreCard).filter(models.ScoreCard.user_id == user.id)
    else:
        raise HTTPException(403, "Admin must use /scores/student/{id}")
    return query.all()


@router.get(
    "/scores/student/{user_id}",
    response_model=List[schemas.ScoreCardOut],
    summary="Admin: view score card by student ID",
    tags=["Score Card"],
)
def get_scores_by_userid(
    user_id: int,
    db: Session = Depends(auth.get_db),
    admin: models.User = Depends(auth.get_current_admin),
):
    query = db.query(models.ScoreCard).filter(models.ScoreCard.user_id == user_id)
    return query.all()


@router.post(
    "/scores",
    response_model=schemas.ScoreCardOut,
    summary="Admin: add/modify score card",
    tags=["Score Card"],
)
def add_or_update_score(
    score: schemas.ScoreCardBase,
    user_id: int,
    db: Session = Depends(auth.get_db),
    admin: models.User = Depends(auth.get_current_admin),
):
    existing = (
        db.query(models.ScoreCard)
        .filter(
            models.ScoreCard.user_id == user_id,
            models.ScoreCard.subject == score.subject,
            models.ScoreCard.exam_name == score.exam_name,
        )
        .first()
    )
    if existing:
        existing.score = score.score
        existing.grade = score.grade
        existing.remarks = score.remarks
        db.commit()
        db.refresh(existing)
        return existing
    db_score = models.ScoreCard(user_id=user_id, **score.dict())
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score


# --- ANNOUNCEMENTS ---


@router.get(
    "/announcements",
    response_model=List[schemas.AnnouncementOut],
    summary="List announcements",
    tags=["Announcements"],
)
def list_announcements(
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    query = db.query(models.Announcement)
    # Student can see only their class or public; admin sees all
    if (
        current_user.role == models.UserRole.student
        and current_user.class_name
    ):
        query = query.filter(
            (models.Announcement.for_class.is_(None))
            | (models.Announcement.for_class == current_user.class_name)
        )
    return query.order_by(models.Announcement.created_at.desc()).all()


@router.post(
    "/announcements",
    response_model=schemas.AnnouncementOut,
    summary="Admin can post announcement",
    tags=["Announcements"],
)
def create_announcement(
    ann: schemas.AnnouncementCreate,
    db: Session = Depends(auth.get_db),
    admin: models.User = Depends(auth.get_current_admin),
):
    db_ann = models.Announcement(**ann.dict(), uploaded_by=admin.id)
    db.add(db_ann)
    db.commit()
    db.refresh(db_ann)
    return db_ann
