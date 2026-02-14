from datetime import date, datetime

from app.db.models import ApplicationStatus, Gender
from pydantic import BaseModel, Field


class AdminApplicationOut(BaseModel):
    id: int
    vacancy_id: int

    full_name: str
    phone: str

    birth_date: date | None
    nationality: str | None
    address: str | None
    gender: Gender | None

    prev_job: str | None
    prev_job_duration: str | None
    prev_job_leave_reason: str | None

    is_married: bool
    source: str | None
    desired_salary: str | None
    why_hire_facts: str | None

    photo_url: str | None

    status: ApplicationStatus
    created_at: datetime

    class Config:
        from_attributes = True


class AdminStatusUpdateIn(BaseModel):
    status: ApplicationStatus = Field(
        ..., description="NEW | IN_REVIEW | REJECTED | ACCEPTED"
    )
