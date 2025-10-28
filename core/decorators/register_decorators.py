from functools import wraps

from aiogram.types import Message, CallbackQuery

from core.db_requests.postgres_requests import get_or_clear_hunter_records
from core.db_requests.redis_requests import get_value_from_cache_by_tg_id
from core.keyboards.inline import main_menu_keyboards
from core.texts import message_texts
from core.texts.special_names import hunter, hunting_base, user_role


def _get_message_by_event(event):
    if isinstance(event, Message):
        return event
    elif isinstance(event, CallbackQuery) and event.message:
        return event.message
    else:
        return  # Не поддерживаемый тип события

def _get_callback_by_event(event):
    if isinstance(event, CallbackQuery):
        return event

def _get_role(db_obj, cache_obj):
    return db_obj or cache_obj

def check_user_registration(get_user_role=False, filter_user_role=None, only_registered=False,
                            only_unregistered=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(event, *args, **kwargs):
            message = _get_message_by_event(event)
            if not message: return
            callback = _get_callback_by_event(event)

            tg_id = event.from_user.id

            cache_obj = await get_value_from_cache_by_tg_id(tg_id)
            db_obj = await get_or_clear_hunter_records(tg_id)

            if not cache_obj and not db_obj:
                await message.answer(message_texts.role_selection,
                                     reply_markup=main_menu_keyboards.role_selection_keyboard())
                if callback: await callback.answer()
                return

            role = _get_role(db_obj, cache_obj)

            if only_registered and not db_obj:
                if callback: await callback.answer(message_texts.unregister)
                return

            if only_unregistered and db_obj:
                if callback: await callback.answer(message_texts.user_already_registered)
                return

            if filter_user_role and filter_user_role != role:
                if callback: await callback.answer(message_texts.wrong_role)
                return

            if get_user_role:
                kwargs[user_role] = role

            return await func(event, *args, **kwargs)
        return wrapper
    return decorator

