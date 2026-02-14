from app.core.settings import settings
from fastapi import Header, HTTPException


def require_internal_token(x_internal_token: str = Header(default="")) -> None:
    """
    Проверяет секретный токен для запросов бот -> backend.
    """
    if not x_internal_token or x_internal_token != settings.internal_api_token:
        raise HTTPException(status_code=403, detail="forbidden")
