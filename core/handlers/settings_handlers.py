from aiogram import Router, F
from aiogram.types import CallbackQuery

from core.db_requests.general_requests import delete_user_by_tg_id
from core.decorators.register_decorators import check_user_registration
from core.handlers.main_menu_handlers import main_menu_callback_query_handler
from core.keyboards.inline.settings_keyboards import main_settings_keyboard
from core.texts import callback_texts, message_texts

router = Router()


@router.callback_query(F.data == callback_texts.settings)
@check_user_registration()
async def main_settings_callback_query_handler(callback: CallbackQuery):
    await callback.message.edit_text(message_texts.main_settings,
                                  reply_markup=main_settings_keyboard())
    await callback.answer()


@router.callback_query(F.data == callback_texts.log_out)
async def log_out_callback_query_handler(callback: CallbackQuery):
    tg_id = callback.from_user.id
    await delete_user_by_tg_id(tg_id)
    await callback.message.answer(message_texts.successful_user_deletion)
    await main_menu_callback_query_handler(callback)
    await callback.answer()
