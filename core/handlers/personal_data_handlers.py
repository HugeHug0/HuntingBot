from aiogram import Router, F
from aiogram.types import CallbackQuery

from core.decorators.register_decorators import check_user_registration
from core.keyboards.inline.personal_data_keyboards import get_personal_data_before_registration_keyboard_by_role
from core.texts import callback_texts, message_texts

router = Router()


@router.callback_query(F.data == callback_texts.personal_data)
@check_user_registration(get_user_role=True)
async def personal_data_callback_query_handler(callback: CallbackQuery, user_role=None):
    await callback.message.answer(text=message_texts.personal_data,
                                  reply_markup=get_personal_data_before_registration_keyboard_by_role(user_role))
    await callback.answer()
