from datetime import date

from app.db.models import Gender, WorkShift
from pydantic import BaseModel, Field


class ApplicationCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    phone: str = Field(min_length=6, max_length=40)

    birth_date: date | None = None
    nationality: str | None = Field(default=None, max_length=80)
    address: str | None = Field(default=None, max_length=255)
    gender: Gender | None = None

    prev_job: str | None = Field(default=None, max_length=255)
    prev_job_duration: str | None = Field(default=None, max_length=80)
    prev_job_leave_reason: str | None = Field(default=None, max_length=255)

    is_married: bool = False
    source: str | None = Field(default=None, max_length=255)
    preferred_shift: WorkShift | None = None
    desired_salary: str | None = Field(default=None, max_length=80)
    why_hire_facts: str | None = None


class ApplicationCreated(BaseModel):
    id: int
