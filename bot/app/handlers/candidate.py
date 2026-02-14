from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.config import settings
from app.keyboards.hr import candidate_start_kb, hr_menu_kb
from app.services.api import BackendClient

router = Router()
api = BackendClient(
    base_url=settings.backend_url,
    internal_token=settings.internal_api_token,
)


@router.message(CommandStart())
async def start_candidate(message: Message) -> None:
    emp = await api.get_employer(message.from_user.id)

    # Если HR (OWNER/RECRUITER) — сразу в HR меню
    if emp.get("is_hr"):
        await message.answer(
            "HR kabinetiga xush kelibsiz!",
            reply_markup=hr_menu_kb(),
        )
        return

    # Иначе — кандидат, предлагаем заполнить анкету
    await message.answer(
        "Assalomu alaykum! 👋\n\n" "Ishga kirish uchun anketani to‘ldiring 👇",
        reply_markup=candidate_start_kb(settings.webapp_url),
    )
