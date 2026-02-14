from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)
from app.config import settings

router = Router()


def candidate_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Anketa to‘ldirish",
                    web_app=WebAppInfo(url=settings.webapp_url),
                )
            ]
        ]
    )


@router.message(CommandStart())
async def start_candidate(message: Message):
    # Если это owner — НЕ перехватываем
    if message.from_user.id == settings.owner_tg_id:
        return

    await message.answer(
        "Assalomu alaykum! 👋\n\n" "Ishga kirish uchun anketani to‘ldiring 👇",
        reply_markup=candidate_kb(),
    )
