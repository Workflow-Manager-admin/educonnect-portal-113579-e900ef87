from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import router

# Ensure all tables are created on startup (production should use Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Exam API",
    description=(
        "API for student exam portal (authentication, timetable, "
        "score card, announcements, uploads)."
    ),
    version="1.0.0",
    openapi_tags=[
        {"name": "Auth", "description": "Authentication endpoints"},
        {"name": "Users", "description": "User management"},
        {"name": "Timetable", "description": "Exam timetable"},
        {"name": "Score Card", "description": "Student scores"},
        {"name": "Announcements", "description": "Announcements board"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}


app.include_router(router)
