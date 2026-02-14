from pathlib import Path

from app.routers.admin import router as admin_router
from app.routers.applications import router as applications_router
from app.routers.internal_admin import router as internal_admin_router
from app.routers.internal_employers import router as internal_employers_router
from app.routers.internal_invites import router as internal_invites_router
from app.routers.vacancies import router as vacancies_router
from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

WEBAPP_DIR = Path(__file__).resolve().parent / "webapp"

app = FastAPI(
    title="HR Bot API",
    docs_url="/docs",
    redoc_url=None,
)

# Роуты
internal_router = APIRouter(prefix="/api/v1/internal")

internal_router.include_router(internal_admin_router)
internal_router.include_router(internal_employers_router)
internal_router.include_router(internal_invites_router)

# public
app.include_router(applications_router)
app.include_router(vacancies_router)
# admin
app.include_router(admin_router)
# internal
app.include_router(internal_router)

# Статика для фото
app.mount("/media", StaticFiles(directory="media"), name="media")


@app.get("/webapp", include_in_schema=False)
def webapp():
    return FileResponse(WEBAPP_DIR / "index.html")


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}
