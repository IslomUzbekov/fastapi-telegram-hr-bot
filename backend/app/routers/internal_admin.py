from app.db.models import Application, ApplicationStatus
from app.db.session import SessionLocal
from app.schemas.admin import AdminApplicationOut, AdminStatusUpdateIn
from app.security.internal_auth import require_internal_token
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/api/internal/admin",
    tags=["internal-admin"],
    dependencies=[Depends(require_internal_token)],
)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _parse_status(status: str) -> ApplicationStatus:
    """
    Принимаем и 'NEW', и 'new' -> приводим к enum ApplicationStatus.
    """
    normalized = status.strip().lower()
    try:
        return ApplicationStatus(normalized)
    except ValueError:
        allowed = [s.value for s in ApplicationStatus]
        raise HTTPException(
            status_code=422,
            detail=f"Invalid status '{status}'. Allowed: {allowed}",
        )


@router.get("/applications", response_model=list[AdminApplicationOut])
def list_applications(
    status: str | None = Query(default=None),
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    q = db.query(Application)

    if status:
        enum_status = _parse_status(status)
        q = q.filter(Application.status == enum_status)

    return (
        q.order_by(
            Application.created_at.desc(),
        )
        .limit(limit)
        .offset(offset)
        .all()
    )


@router.get(
    "/applications/{application_id}",
    response_model=AdminApplicationOut,
)
def get_application(application_id: int, db: Session = Depends(get_db)):
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
def update_status(
    application_id: int, payload: AdminStatusUpdateIn, db: Session = Depends(get_db)
):
    app = (
        db.query(Application)
        .join(Candidate, Candidate.id == Application.candidate_id)
        .filter(Application.id == application_id)
        .one_or_none()
    )
    if app is None:
        raise HTTPException(status_code=404, detail="not found")

    app.status = payload.status
    db.commit()

    # notify candidate about decision / progress
    try:
        msg = _status_message(payload.status)
        _send_telegram_plain_message(
            bot_token=settings.bot_token,
            chat_id=app.candidate.tg_user_id,
            text=msg,
        )
    except Exception:
        pass

    status_out = app.status.value if hasattr(app.status, "value") else app.status
    return {"ok": True, "id": app.id, "status": status_out}


def _status_message(status: ApplicationStatus) -> str:
    if status == ApplicationStatus.ACCEPTED:
        return "✅ Arizangiz qabul qilindi!\n\nTez orada siz bilan bog‘lanamiz."
    if status == ApplicationStatus.REJECTED:
        return "❌ Afsus, arizangiz rad etildi.\n\nKeyingi safar omad!"
    if status == ApplicationStatus.IN_REVIEW:
        return "🕒 Arizangiz ko‘rib chiqilmoqda.\n\nTez orada javob beramiz."
    return "ℹ️ Arizangiz holati yangilandi."
