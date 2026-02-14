from app.db.models import Employer
from app.db.session import SessionLocal
from app.security.internal_auth import require_internal_token
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/api/internal/employers",
    tags=["internal-employers"],
    dependencies=[Depends(require_internal_token)],
)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/by-tg/{tg_user_id}")
def get_employer_by_tg(
    tg_user_id: int,
    db: Session = Depends(get_db),
):
    emp = (
        db.query(Employer)
        .filter(
            Employer.tg_user_id == tg_user_id,
            Employer.is_active == True,
        )
        .one_or_none()
    )

    if not emp:
        return {"is_hr": False, "role": None}

    return {
        "is_hr": True,
        "role": emp.role.value,  # важно!
    }
