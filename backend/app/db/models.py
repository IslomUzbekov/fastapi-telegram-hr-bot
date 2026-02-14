from __future__ import annotations

import enum
from datetime import date, datetime

from app.db.base import Base
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ApplicationStatus(str, enum.Enum):
    NEW = "new"
    IN_REVIEW = "in_review"
    REJECTED = "rejected"
    ACCEPTED = "accepted"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class WorkShift(str, enum.Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    FLEX = "flex"


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    applications: Mapped[list["Application"]] = relationship(
        back_populates="vacancy",
    )


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_user_id: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, nullable=False
    )
    tg_username: Mapped[str | None] = mapped_column(String(80), nullable=True)

    applications: Mapped[list["Application"]] = relationship(
        back_populates="candidate",
    )


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )
    vacancy_id: Mapped[int] = mapped_column(
        ForeignKey("vacancies.id"),
        nullable=False,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    phone: Mapped[str] = mapped_column(String(40), nullable=False)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(80), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gender: Mapped[Gender | None] = mapped_column(
        Enum(Gender, name="gender_enum"),
        nullable=True,
    )

    # Previous work experience
    prev_job: Mapped[str | None] = mapped_column(String(255), nullable=True)
    prev_job_duration: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )
    prev_job_leave_reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    is_married: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    desired_salary: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )
    preferred_shift: Mapped[WorkShift | None] = mapped_column(
        Enum(WorkShift, name="workshift_enum"),
        nullable=True,
    )
    why_hire_facts: Mapped[str | None] = mapped_column(Text, nullable=True)

    photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="applicationstatus"),
        default=ApplicationStatus.NEW,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    candidate: Mapped["Candidate"] = relationship(
        back_populates="applications",
    )
    vacancy: Mapped["Vacancy"] = relationship(back_populates="applications")


class EmployerRole(str, enum.Enum):
    OWNER = "OWNER"
    RECRUITER = "RECRUITER"


class Employer(Base):
    __tablename__ = "employers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_user_id: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, nullable=False
    )
    role: Mapped[EmployerRole] = mapped_column(
        Enum(EmployerRole, name="employer_role"),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


class EmployerInvite(Base):
    __tablename__ = "employer_invites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )

    role: Mapped[EmployerRole] = mapped_column(
        Enum(EmployerRole, name="employerrole"),
        nullable=False,
    )

    is_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
