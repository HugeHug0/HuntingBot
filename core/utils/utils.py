from datetime import datetime

import phonenumbers
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from core.keyboards.inline.main_menu_keyboards import main_menu_hunting_base_keyboard, main_menu_hunter_keyboard
from core.texts.special_names import hunting_base, hunter
from email_validator import validate_email, EmailNotValidError


def get_keyboard_by_user_role(user_role):
    if user_role == hunter:
        return main_menu_hunter_keyboard
    elif user_role == hunting_base:
        return main_menu_hunting_base_keyboard

def is_phone_number(text: str) -> bool:
    try:
        number = phonenumbers.parse(text, None)  # None — не указываем страну
        return phonenumbers.is_possible_number(number) and phonenumbers.is_valid_number(number)
    except phonenumbers.NumberParseException:
        return False

def is_valid_email(email: str) -> bool:
    try:
        validate_email(email)  # проверяет синтаксис и нормализует
        return True
    except EmailNotValidError:
        return False

def is_valid_period(period: str) -> bool:
    try:
        start_str, end_str = period.split()
        start = datetime.strptime(start_str, "%Y-%m-%d").date()
        end = datetime.strptime(end_str, "%Y-%m-%d").date()
        return start <= end  # период валиден, если первая дата не позже второй
    except Exception:
        return False

async def send_text_to_group(bot: Bot, chat_id: int | str, text: str):
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        return True
    except TelegramAPIError as e:
        print(f"Ошибка Telegram API: {e}")
    except Exception as e:
        print(f"Не удалось отправить сообщение: {e}")
    return False

async def hunter_format_registration_text(state) -> str:
    data = await state.get_data()
    return (
        "✅ Регистрация завершена\n\n"
        f"👤 ФИО: {data.get('full_name')}\n"
        f"📞 Телефон: {data.get('phone_number')}\n"
        f"📧 E-mail: {data.get('email', '—')}\n"
        f"🌍 Регион охоты: {data.get('region')}\n"
        f"🏹 Вид охоты: {data.get('hunting_type')}\n"
        f"📅 Период: {' / '.join(data.get('hunting_date').split())}\n"
        f"📝 Комментарий: {data.get('comment', '—')}"
    )

def get_format_services_selected(selected: list[str] | set[str]) -> str:
    """Форматирует сообщение о количестве выбранных услуг."""
    if not selected:
        return "❌ Услуги не выбраны."

    selected = list(selected)
    return f"✅ Выбрано услуг: {len(selected)}\n" + "\n".join(f"• {s}" for s in selected)

async def get_services_selected(state, key):
    data = await state.get_data()
    selected = set(data.get("services", []))  # используем set, чтобы не было дублей

    if key in selected:
        selected.remove(key)
    else:
        selected.add(key)

    return selected