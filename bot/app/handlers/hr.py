from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message
from app.config import settings
from app.keyboards.hr import (
    application_actions_kb,
    applications_list_kb,
    candidate_start_kb,
    hr_menu_kb,
)
from app.services.api import BackendClient

router = Router()

api = BackendClient(
    base_url=settings.backend_url, internal_token=settings.internal_api_token
)


async def require_hr(user_id: int) -> bool:
    """
    Разрешено: OWNER и RECRUITER (любой активный HR).
    """
    emp = await api.get_employer(user_id)
    return bool(emp.get("is_hr"))


async def require_owner(user_id: int) -> bool:
    """
    Разрешено: только OWNER.
    """
    emp = await api.get_employer(user_id)
    return emp.get("is_hr") is True and emp.get("role") == "OWNER"


@router.message(CommandStart(deep_link=True))
async def cmd_start(message: Message, command: CommandObject) -> None:
    args = (command.args or "").strip()

    # 1) join by invite
    if args.startswith("invite_"):
        token = args.replace("invite_", "", 1)
        try:
            res = await api.join_invite(message.from_user.id, token)
            await message.answer(
                f"✅ Siz HR sifatida qo‘shildingiz. Role: {res.get('role')}"
            )
        except Exception:
            await message.answer(
                "❌ Taklif havolasi noto‘g‘ri yoki ishlatilgan.",
            )
            return

    # 2) обычная логика: если HR -> HR меню, иначе -> кандидат меню
    emp = await api.get_employer(message.from_user.id)
    if emp.get("is_hr"):
        await message.answer(
            "HR kabinetiga xush kelibsiz!",
            reply_markup=hr_menu_kb(),
        )
    else:
        await message.answer(
            "Assalomu alaykum! Anketani to‘ldiring 👇",
            reply_markup=candidate_start_kb(settings.webapp_url),
        )


@router.callback_query(F.data == "hr:menu")
async def hr_menu(cb: CallbackQuery) -> None:
    if not await require_hr(cb.from_user.id):
        await cb.answer("Ruxsat yo'q", show_alert=True)
        return

    await cb.message.edit_text(
        "HR kabinetiga xush kelibsiz! Quyidagi menyudan bo'limni tanlang:",
        reply_markup=hr_menu_kb(),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("hr:list:"))
async def hr_list(cb: CallbackQuery) -> None:
    if not await require_hr(cb.from_user.id):
        await cb.answer("Ruxsat yo'q", show_alert=True)
        return

    status = cb.data.split(":")[-1]
    rows = await api.list_applications(status=status, limit=20, offset=0)

    if not rows:
        await cb.message.edit_text(
            f"Arizalar {status} statusida yo'q.", reply_markup=hr_menu_kb()
        )
        await cb.answer()
        return

    await cb.message.edit_text(
        f"📄 Arizalar ({status}):",
        reply_markup=applications_list_kb(rows),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("hr:status:"))
async def hr_set_status(cb: CallbackQuery) -> None:
    if not await require_hr(cb.from_user.id):
        await cb.answer("Ruxsat yo'q", show_alert=True)
        return

    _, _, app_id_str, status = cb.data.split(":")
    app_id = int(app_id_str)

    await api.set_status(app_id, status=status)
    updated = await api.get_application(app_id)

    await cb.answer("Status yangilandi ✅")

    text = (
        f"🧑‍💼 Ariza #{updated['id']}\n\n"
        f"👤 F.I.SH: {updated['full_name']}\n"
        f"📞 Telefon: {updated['phone']}\n"
        f"🎂 Tug‘ilgan sana: {updated.get('birth_date') or '-'}\n"
        f"🌍 Millat: {updated.get('nationality') or '-'}\n"
        f"📍 Manzil: {updated.get('address') or '-'}\n"
        f"🚻 Jins: {updated.get('gender') or '-'}\n\n"
        f"🏢 Oldin ishlagan joy: {updated.get('prev_job') or '-'}\n"
        f"⏳ Ish muddati: {updated.get('prev_job_duration') or '-'}\n"
        f"📌 Bo‘shash sababi: {updated.get('prev_job_leave_reason') or '-'}\n\n"
        f"💍 Oilali: {'Ha' if updated.get('is_married') else 'Yo‘q'}\n"
        f"🔎 Qayerdan bildi: {updated.get('source') or '-'}\n"
        f"💰 Istagan maosh: {updated.get('desired_salary') or '-'}\n\n"
        f"⭐ Nega ishga olish kerak:\n{updated.get('why_hire_facts') or '-'}\n\n"
        f"📊 Status: {updated['status']}"
    )

    photo_url = updated.get("photo_url")
    if photo_url:
        await cb.message.answer_photo(
            photo=f"{settings.backend_url}{photo_url}",
            caption=text,
            reply_markup=application_actions_kb(app_id),
        )
    else:
        await cb.message.answer(
            text,
            reply_markup=application_actions_kb(app_id),
        )


@router.callback_query(F.data.startswith("hr:open:"))
async def hr_open_app(cb: CallbackQuery) -> None:
    if not await require_hr(cb.from_user.id):
        await cb.answer("Ruxsat yo'q", show_alert=True)
        return

    app_id = int(cb.data.split(":")[-1])
    data = await api.get_application(app_id)

    text = (
        f"🧑‍💼 Ariza #{data['id']}\n\n"
        f"👤 F.I.SH: {data['full_name']}\n"
        f"📞 Telefon: {data['phone']}\n"
        f"🎂 Tug‘ilgan sana: {data.get('birth_date') or '-'}\n"
        f"🌍 Millat: {data.get('nationality') or '-'}\n"
        f"📍 Manzil: {data.get('address') or '-'}\n"
        f"🚻 Jins: {data.get('gender') or '-'}\n\n"
        f"🏢 Oldin ishlagan joy: {data.get('prev_job') or '-'}\n"
        f"⏳ Ish muddati: {data.get('prev_job_duration') or '-'}\n"
        f"📌 Bo‘shash sababi: {data.get('prev_job_leave_reason') or '-'}\n\n"
        f"💍 Oilali: {'Ha' if data.get('is_married') else 'Yo‘q'}\n"
        f"🔎 Qayerdan bildi: {data.get('source') or '-'}\n"
        f"💰 Istagan maosh: {data.get('desired_salary') or '-'}\n\n"
        f"⭐ Nega ishga olish kerak:\n{data.get('why_hire_facts') or '-'}\n\n"
        f"📊 Status: {data['status']}"
    )

    photo_url = data.get("photo_url")
    if photo_url:
        await cb.message.answer_photo(
            photo=f"{settings.backend_url}{photo_url}",
            caption=text,
            reply_markup=application_actions_kb(app_id),
        )
    else:
        await cb.message.answer(
            text,
            reply_markup=application_actions_kb(app_id),
        )

    await cb.answer()


@router.callback_query(F.data == "hr:add_recruiter")
async def add_recruiter(cb: CallbackQuery):
    emp = await api.get_employer(cb.from_user.id)
    if not (emp.get("is_hr") and emp.get("role") == "OWNER"):
        await cb.answer("Faqat OWNER", show_alert=True)
        return

    inv = await api.create_invite(cb.from_user.id, role="RECRUITER")
    token = inv["token"]
    bot_username = (await cb.bot.me()).username
    link = f"https://t.me/{bot_username}?start=invite_{token}"

    await cb.message.answer(f"🔗 HR uchun havola:\n{link}")
    await cb.answer()
