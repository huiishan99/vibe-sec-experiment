"""
Minimal FastAPI application that accepts an e‑mail address via POST
and stores it in a SQLite database.

Requirements:
    pip install fastapi uvicorn email-validator sqlalchemy

Run the server:
    uvicorn main:app --reload
"""

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# --------------------------------------------------------------------------- #
# Database setup
# --------------------------------------------------------------------------- #

# SQLite database file in the same directory as this script
DB_FILE = Path(__file__).with_name("emails.db")
DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


class EmailRecord(Base):
    """SQLAlchemy model for storing e‑mail addresses."""
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# Create tables on first run
Base.metadata.create_all(bind=engine)

# --------------------------------------------------------------------------- #
# FastAPI application
# --------------------------------------------------------------------------- #

app = FastAPI(title="Email Storage API")


class EmailIn(BaseModel):
    """Request body schema – validates that the field is a proper e‑mail."""
    email: EmailStr


class EmailOut(BaseModel):
    """Response body schema."""
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


@app.post(
    "/emails",
    response_model=EmailOut,
    status_code=status.HTTP_201_CREATED,
    summary="Store an e‑mail address",
)
def create_email(payload: EmailIn):
    """
    Accepts a JSON payload with an e‑mail address, validates it,
    and stores it in the SQLite database.
    """
    db: Session = SessionLocal()
    try:
        record = EmailRecord(email=payload.email)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )
    finally:
        db.close()


@app.get(
    "/emails/{email_id}",
    response_model=EmailOut,
    summary="Retrieve a stored e‑mail by ID",
)
def get_email(email_id: int):
    """
    Retrieve a stored e‑mail record by its database ID.
    """
    db: Session = SessionLocal()
    try:
        record = db.query(EmailRecord).filter(EmailRecord.id == email_id).first()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found",
            )
        return record
    finally:
        db.close()


# --------------------------------------------------------------------------- #
# Optional: health check endpoint
# --------------------------------------------------------------------------- #

@app.get("/health", summary="Health check")
def health_check():
    """Simple health check that verifies DB connectivity."""
    try:
        db: Session = SessionLocal()
        db.execute("SELECT 1")
        return {"status": "ok"}
    finally:
        db.close()


# --------------------------------------------------------------------------- #
# Run with: uvicorn main:app --reload
# --------------------------------------------------------------------------- #