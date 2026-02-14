from app.db.models import Vacancy
from app.db.session import SessionLocal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/vacancies", tags=["vacancies"])


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def list_vacancies(db: Session = Depends(get_db)):
    rows = db.query(Vacancy).filter(Vacancy.is_active == True).all()
    return [
        {
            "id": v.id,
            "title": v.title,
            "description": v.description,
        }
        for v in rows
    ]
