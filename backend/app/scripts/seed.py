import os

from app.db.models import Employer, EmployerRole, Vacancy
from app.db.session import SessionLocal


def _env_int(name: str, default: int | None = None) -> int | None:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def main() -> None:
    db = SessionLocal()
    try:
        # 1) Owner employer
        owner_tg_id = _env_int("OWNER_TG_ID") or _env_int("OWNER_TG_USER_ID")
        if owner_tg_id:
            employer = (
                db.query(Employer)
                .filter(Employer.tg_user_id == owner_tg_id)
                .one_or_none()
            )
            if employer is None:
                employer = Employer(
                    tg_user_id=owner_tg_id,
                    role=EmployerRole.OWNER,
                    is_active=True,
                )
                db.add(employer)
            else:
                employer.role = EmployerRole.OWNER
                employer.is_active = True

        # 2) Default vacancy (optional)
        v = (
            db.query(Vacancy)
            .filter(
                Vacancy.title == "Umumiy ariza",
            )
            .one_or_none()
        )
        if v is None:
            db.add(
                Vacancy(
                    title="Umumiy ariza",
                    description="Default application",
                )
            )

        db.commit()
        print("✅ Seed done: owner + default vacancy")
    finally:
        db.close()


if __name__ == "__main__":
    main()
