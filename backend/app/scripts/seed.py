import os
from datetime import datetime

from app.db.models import (
    Application,
    ApplicationStatus,
    Candidate,
    Employer,
    EmployerRole,
    Vacancy,
)
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
        owner_tg_id = _env_int("OWNER_TG_ID") or _env_int(
            "OWNER_TG_USER_ID"
        )  # на всякий случай
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

        # 2) Vacancies
        vacancies = [
            ("Kassir", True),
            ("Omborchi", True),
            ("Sotuvchi", True),
        ]

        vacancy_ids: list[int] = []
        for title, is_active in vacancies:
            v = db.query(Vacancy).filter(Vacancy.title == title).one_or_none()
            if v is None:
                v = Vacancy(title=title, is_active=is_active)
                db.add(v)
                db.flush()  # чтобы получить v.id
            vacancy_ids.append(v.id)

        # 3) Candidate (test)
        test_candidate_tg_id = _env_int("TEST_CANDIDATE_TG_ID", 900000001)
        candidate = (
            db.query(Candidate)
            .filter(Candidate.tg_user_id == test_candidate_tg_id)
            .one_or_none()
        )
        if candidate is None:
            candidate = Candidate(
                tg_user_id=test_candidate_tg_id, tg_username="test_candidate"
            )
            db.add(candidate)
            db.flush()

        # 4) Applications (test)
        # создадим 2 заявки в статусе NEW (value = "new")
        exists = (
            db.query(Application)
            .filter(Application.candidate_id == candidate.id)
            .count()
        )

        if exists == 0:
            a1 = Application(
                candidate_id=candidate.id,
                vacancy_id=vacancy_ids[0],
                full_name="Test Candidate One",
                phone="+998901112233",
                city="Tashkent",
                skills="Mas'uliyatli, tez o‘rganaman",
                experience_text="1 yil kassir bo‘lib ishlaganman",
                photo_url=None,
                status=ApplicationStatus.NEW,
                created_at=datetime.utcnow(),
            )
            a2 = Application(
                candidate_id=candidate.id,
                vacancy_id=vacancy_ids[1],
                full_name="Test Candidate One",
                phone="+998901112233",
                city="Tashkent",
                skills="Tartibli, intizomli",
                experience_text="Ombor hisobini yuritganman",
                photo_url=None,
                status=ApplicationStatus.NEW,
                created_at=datetime.utcnow(),
            )
            db.add_all([a1, a2])

        db.commit()
        print("✅ Seed done: employer, vacancies, candidate, applications")
    finally:
        db.close()


if __name__ == "__main__":
    main()
