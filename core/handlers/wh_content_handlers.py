from aiogram import Router, F
from aiogram.types import CallbackQuery

from core.decorators.register_decorators import check_user_registration
from core.keyboards.inline.wh_content_keyboards import wh_content_main_keyboard
from core.texts import callback_texts, message_texts

router = Router()


@router.callback_query(F.data == callback_texts.wh_content)
@check_user_registration()
async def wh_content_callback_query_handler(callback: CallbackQuery):
    await callback.message.edit_text(message_texts.wh_main_content, reply_markup=wh_content_main_keyboard())

