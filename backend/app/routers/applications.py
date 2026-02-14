from __future__ import annotations

import json
import uuid
from pathlib import Path

import httpx
from app.core.settings import settings
from app.db.models import Application, Candidate, Employer, Vacancy
from app.db.session import SessionLocal
from app.schemas.applications import ApplicationCreate, ApplicationCreated
from app.security.telegram_webapp import verify_telegram_init_data
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Header,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/applications", tags=["applications"])


def get_db() -> Session:
    """
    Dependency для получения DB-сессии.

    Yields:
        Session: SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_tg_user_id(x_tg_init_data: str = Header(default="")) -> int:
    """
    Извлекает tg_user_id из initData и проверяет подпись.

    Args:
        x_tg_init_data: заголовок X-Tg-Init-Data

    Returns:
        int: telegram user id

    Raises:
        HTTPException: 401 если initData невалиден
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


@router.post("", response_model=ApplicationCreated)
def create_application(
    data: ApplicationCreate,
    background_tasks: BackgroundTasks,
    tg_user_id: int = Depends(get_tg_user_id),
    db: Session = Depends(get_db),
) -> ApplicationCreated:

    # --- get or create candidate ---
    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.tg_user_id == tg_user_id,
        )
        .one_or_none()
    )

    if candidate is None:
        candidate = Candidate(tg_user_id=tg_user_id)
        db.add(candidate)
        db.flush()

    # --- get or create default vacancy ---
    vacancy = (
        db.query(Vacancy)
        .filter(
            Vacancy.title == "Umumiy ariza",
        )
        .one_or_none()
    )

    if vacancy is None:
        vacancy = Vacancy(
            title="Umumiy ariza",
            description="Default application",
        )
        db.add(vacancy)
        db.flush()

    app = Application(
        candidate_id=candidate.id,
        vacancy_id=vacancy.id,
        full_name=data.full_name,
        phone=data.phone,
        birth_date=data.birth_date,
        nationality=data.nationality,
        address=data.address,
        gender=data.gender,
        prev_job=data.prev_job,
        prev_job_duration=data.prev_job_duration,
        prev_job_leave_reason=data.prev_job_leave_reason,
        is_married=data.is_married,
        source=data.source,
        desired_salary=data.desired_salary,
        why_hire_facts=data.why_hire_facts,
    )

    db.add(app)
    db.commit()
    db.refresh(app)

    # уведомляем всех активных работодателей
    employers = db.query(Employer).filter(Employer.is_active == True).all()

    text = _format_new_application_text(app)
    for emp in employers:
        background_tasks.add_task(
            _send_telegram_message,
            settings.bot_token,
            emp.tg_user_id,
            text,
            app.id,
        )

    return ApplicationCreated(id=app.id)


@router.post("/{application_id}/photo")
async def upload_photo(
    application_id: int,
    photo: UploadFile = File(...),
    tg_user_id: int = Depends(get_tg_user_id),
    db: Session = Depends(get_db),
):
    """
    Загрузка фото для конкретной заявки.
    Проверяем, что заявка принадлежит текущему tg_user_id.
    Сохраняем файл локально в media/photos.

    Returns:
        dict: photo_url
    """
    app = (
        db.query(Application)
        .join(Candidate, Candidate.id == Application.candidate_id)
        .filter(
            Application.id == application_id,
            Candidate.tg_user_id == tg_user_id,
        )
        .one_or_none()
    )
    if app is None:
        raise HTTPException(status_code=404, detail="application not found")

    allowed = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    if photo.content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Only jpg, png, webp allowed",
        )

    content = await photo.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Max file size is 5MB")

    media_root = Path(settings.media_root)
    photos_dir = media_root / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)

    ext = allowed[photo.content_type]
    filename = f"{application_id}_{uuid.uuid4().hex}{ext}"
    filepath = photos_dir / filename
    filepath.write_bytes(content)

    app.photo_url = f"/media/photos/{filename}"
    db.commit()

    # уведомляем всех активных работодателей, что фото загружено
    employers = db.query(Employer).filter(Employer.is_active == True).all()

    caption = f"📸 Rasm yuklandi — Ariza #{app.id}\n" + _format_new_application_text(
        app
    )

    public_photo = f"{settings.backend_url}{app.photo_url}"
    for emp in employers:
        background_tasks.add_task(
            _send_telegram_photo,
            settings.bot_token,
            emp.tg_user_id,
            public_photo,
            caption,
            app.id,
        )

    return {"photo_url": app.photo_url}


def _format_new_application_text(app: Application) -> str:
    parts = [
        f"🆕 Yangi ariza #{app.id}",
        f"👤 F.I.SH: {app.full_name}",
        f"📞 Telefon: {app.phone}",
    ]

    if app.birth_date:
        parts.append(
            f"🎂 Tug‘ilgan sana: {app.birth_date.strftime('%d.%m.%Y')}",
        )
    if app.nationality:
        parts.append(f"🌍 Millat: {app.nationality}")
    if app.address:
        parts.append(f"📍 Manzil: {app.address}")
    if app.gender:
        parts.append(
            f"🚻 Jins: {app.gender.value if hasattr(app.gender, 'value') else app.gender}"
        )

    if app.prev_job:
        parts.append(f"🏢 Oldin ishlagan joy: {app.prev_job}")
    if app.prev_job_duration:
        parts.append(f"⏳ Ish muddati: {app.prev_job_duration}")
    if app.prev_job_leave_reason:
        parts.append(f"📌 Nega bo‘shagan: {app.prev_job_leave_reason}")

    parts.append(f"💍 Oilali: {'Ha' if app.is_married else 'Yo‘q'}")

    if app.source:
        parts.append(f"🔎 Qayerdan bildi: {app.source}")
    if app.desired_salary:
        parts.append(f"💰 Istagan maosh: {app.desired_salary}")
    if app.why_hire_facts:
        parts.append(f"⭐ Nega ishga olish kerak: {app.why_hire_facts}")

    parts.append("\nBot orqali ko‘rish: HR menyu → Arizalar")
    return "\n".join(parts)


def _hr_open_kb(application_id: int) -> dict:
    """
    Inline keyboard, чтобы бот поймал callback: hr:open:<id>
    """
    return {
        "inline_keyboard": [
            [
                {
                    "text": "👀 Ko‘rish",
                    "callback_data": f"hr:open:{application_id}",
                }
            ]
        ]
    }


def _send_telegram_message(
    bot_token: str,
    chat_id: int,
    text: str,
    application_id: int,
) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
        "reply_markup": _hr_open_kb(application_id),
    }
    # sync-запрос (мы вызовем через BackgroundTasks, чтобы не тормозить ответ)
    with httpx.Client(timeout=10) as client:
        r = client.post(url, json=payload)
        r.raise_for_status()


def _send_telegram_photo(
    bot_token: str,
    chat_id: int,
    photo_url: str,
    caption: str,
    application_id: int,
) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption[:1024],  # лимит Telegram
        "reply_markup": _hr_open_kb(application_id),
    }
    with httpx.Client(timeout=10) as client:
        r = client.post(url, json=payload)
        r.raise_for_status()
