import hashlib
import hmac
from urllib.parse import parse_qsl


def verify_telegram_init_data(init_data: str, bot_token: str) -> dict:
    """
    Проверяет подпись initData от Telegram WebApp.
    Возвращает словарь параметров (без hash), если подпись верна.

    Args:
        init_data: строка window.Telegram.WebApp.initData
        bot_token: токен бота

    Returns:
        dict: параметры initData

    Raises:
        ValueError: если initData пустой/некорректный/подпись не совпала
    """
    if not init_data:
        raise ValueError("init_data is empty")

    data = dict(parse_qsl(init_data, keep_blank_values=True))

    received_hash = data.pop("hash", None)
    if not received_hash:
        raise ValueError("hash is missing")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))

    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()

    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise ValueError("init_data signature is invalid")

    return data
