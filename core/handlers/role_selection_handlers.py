from aiogram import Router, F
from aiogram.types import CallbackQuery

from core.db.redis import redis_client
from core.handlers.main_menu_handlers import main_menu_callback_query_handler
from core.texts import callback_texts, message_texts
from core.texts.special_names import hunter, hunting_base

router = Router()

@router.callback_query(F.data == callback_texts.hunter_role_select)
async def hunter_role_select_callback_query_handler(callback: CallbackQuery):
    tg_id = callback.from_user.id
    await redis_client.set(f"user:{tg_id}", hunter, ex=60 * 60 * 24 * 2)
    await callback.message.answer(message_texts.hunter_role_about)

    await main_menu_callback_query_handler(callback, answer_menu=True)


@router.callback_query(F.data == callback_texts.hunting_base_role_select)
async def hunting_base_role_select_callback_query_handler(callback: CallbackQuery):
    tg_id = callback.from_user.id
    await redis_client.set(f"user:{tg_id}", hunting_base, ex=60 * 60 * 24 * 2)
    await callback.message.answer(message_texts.hunting_role_role_about)

    await main_menu_callback_query_handler(callback, answer_menu=True)

