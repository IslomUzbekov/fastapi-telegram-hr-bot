import asyncio

from aiogram import Bot, Dispatcher
from app.config import settings
from app.handlers.candidate import router as candidate_router
from app.handlers.hr import router as hr_router


async def main() -> None:
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.include_router(candidate_router)
    dp.include_router(hr_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
