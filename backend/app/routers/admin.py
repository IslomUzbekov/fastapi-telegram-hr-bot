from __future__ import annotations

import json

from app.core.settings import settings
from app.db.models import Application, ApplicationStatus, Candidate, Employer
from app.db.session import SessionLocal
from app.schemas.admin import AdminApplicationOut, AdminStatusUpdateIn
from app.security.telegram_webapp import verify_telegram_init_data
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/admin", tags=["admin"])


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_tg_user_id(x_tg_init_data: str = Header(default="")) -> int:
    """
    Достаём tg_user_id из Telegram WebApp initData.
    Работает для WebApp. Для бота сделаем internal token позже.
    """
    try:
        payload = verify_telegram_init_data(x_tg_init_data, settings.bot_token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    user_raw = payload.get("user")
    if not user_raw:
        raise HTTPException(
            status_code=401,
            detail="user is missing in init_data",
        )

    user = json.loads(user_raw)
    tg_user_id = user.get("id")
    if not tg_user_id:
        raise HTTPException(
            status_code=401,
            detail="telegram user id not found",
        )

    return int(tg_user_id)


def require_employer(
    tg_user_id: int = Depends(get_tg_user_id),
    db: Session = Depends(get_db),
) -> Employer:
    """
    Доступ только тем, кто есть в таблице employers и активен.
    """
    employer = (
        db.query(Employer)
        .filter(
            Employer.tg_user_id == tg_user_id,
            Employer.is_active == True,
        )  # noqa: E712
        .one_or_none()
    )
    if employer is None:
        raise HTTPException(status_code=403, detail="forbidden")
    return employer


@router.get("/applications", response_model=list[AdminApplicationOut])
def list_applications(
    status: ApplicationStatus | None = None,
    vacancy_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
    _employer: Employer = Depends(require_employer),
    db: Session = Depends(get_db),
):
    """
    Список заявок.
    Фильтры: status, vacancy_id
    Пагинация: limit/offset
    """
    q = db.query(Application).join(Candidate)

    if status is not None:
        q = q.filter(Application.status == status)
    if vacancy_id is not None:
        q = q.filter(Application.vacancy_id == vacancy_id)

    q = q.order_by(Application.created_at.desc()).limit(limit).offset(offset)

    return q.all()


@router.get(
    "/applications/{application_id}",
    response_model=AdminApplicationOut,
)
def get_application(
    application_id: int,
    _employer: Employer = Depends(require_employer),
    db: Session = Depends(get_db),
):
    """
    Карточка заявки.
    """
    app = (
        db.query(Application)
        .filter(
            Application.id == application_id,
        )
        .one_or_none()
    )
    if app is None:
        raise HTTPException(status_code=404, detail="not found")
    return app


@router.patch("/applications/{application_id}/status")
def update_application_status(
    application_id: int,
    payload: AdminStatusUpdateIn,
    _employer: Employer = Depends(require_employer),
    db: Session = Depends(get_db),
):
    """
    Смена статуса заявки.
    """
    app = (
        db.query(Application)
        .filter(
            Application.id == application_id,
        )
        .one_or_none()
    )
    if app is None:
        raise HTTPException(status_code=404, detail="not found")

    app.status = payload.status
    db.commit()
    return {"ok": True, "id": app.id, "status": app.status}
