from __future__ import annotations

import secrets

from app.db.models import Employer, EmployerInvite, EmployerRole
from app.db.session import SessionLocal
from app.security.internal_auth import require_internal_token
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/api/internal/invites",
    tags=["internal-invites"],
    dependencies=[Depends(require_internal_token)],
)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class InviteCreateIn(BaseModel):
    tg_user_id: int
    role: EmployerRole = EmployerRole.RECRUITER


class InviteJoinIn(BaseModel):
    tg_user_id: int
    token: str


@router.post("/create")
def create_invite(payload: InviteCreateIn, db: Session = Depends(get_db)):
    owner = (
        db.query(Employer)
        .filter(
            Employer.tg_user_id == payload.tg_user_id,
            Employer.is_active == True,
        )
        .one_or_none()
    )
    if not owner or owner.role != EmployerRole.OWNER:
        raise HTTPException(status_code=403, detail="owner only")

    token = secrets.token_urlsafe(24)

    inv = EmployerInvite(token=token, role=payload.role, is_used=False)
    db.add(inv)
    db.commit()

    return {"ok": True, "token": token, "role": inv.role.value}


@router.post("/join")
def join_invite(payload: InviteJoinIn, db: Session = Depends(get_db)):
    inv = (
        db.query(EmployerInvite)
        .filter(
            EmployerInvite.token == payload.token,
            EmployerInvite.is_used == False,
        )
        .one_or_none()
    )
    if not inv:
        raise HTTPException(
            status_code=404,
            detail="invite not found or already used",
        )

    emp = (
        db.query(Employer)
        .filter(
            Employer.tg_user_id == payload.tg_user_id,
        )
        .one_or_none()
    )
    if emp:
        emp.role = inv.role
        emp.is_active = True
    else:
        emp = Employer(
            tg_user_id=payload.tg_user_id,
            role=inv.role,
            is_active=True,
        )
        db.add(emp)

    inv.is_used = True
    db.commit()

    return {"ok": True, "role": emp.role.value}
