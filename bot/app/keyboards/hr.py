from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def hr_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🆕 Yangi", callback_data="hr:list:new")
    b.button(text="👀 Ko'rib chiqish", callback_data="hr:list:in_review")
    b.button(text="✅ Qabul qilish", callback_data="hr:list:accepted")
    b.button(text="❌ Rad etish", callback_data="hr:list:rejected")
    b.button(text="➕ HR qo‘shish", callback_data="hr:add_recruiter")
    b.adjust(2, 2)
    return b.as_markup()


def application_actions_kb(app_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.add(
        InlineKeyboardButton(
            text="👀 Ko'rib chiqish",
            callback_data=f"hr:status:{app_id}:in_review",
        ),
        InlineKeyboardButton(
            text="✅ Qabul qilish", callback_data=f"hr:status:{app_id}:accepted"
        ),
        InlineKeyboardButton(
            text="❌ Rad etish", callback_data=f"hr:status:{app_id}:rejected"
        ),
    )
    b.adjust(2, 1)
    b.row(InlineKeyboardButton(text="⬅️ Menu", callback_data="hr:menu"))
    return b.as_markup()


def applications_list_kb(rows):
    kb = InlineKeyboardBuilder()

    for r in rows[:10]:
        kb.button(
            text=f"#{r['id']} — {r['full_name']}",
            callback_data=f"hr:open:{r['id']}",
        )

    kb.button(text="⬅️ Menu", callback_data="hr:menu")

    kb.adjust(1)
    return kb.as_markup()


def candidate_start_kb(webapp_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Anketa to‘ldirish",
                    web_app=WebAppInfo(url=webapp_url),
                )
            ]
        ]
    )
