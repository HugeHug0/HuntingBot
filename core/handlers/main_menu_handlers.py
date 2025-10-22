from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from core.decorators.register_decorators import check_user_registration
from core.filters.chat_type_filters import PrivateChatFilter, private
from core.texts import message_texts, callback_texts
from core.utils.utils import get_keyboard_by_user_role

router = Router()


@router.message(StateFilter(None), PrivateChatFilter([private]))
@check_user_registration(get_user_role=True)
async def main_menu_handler(message: Message, user_role=None):
    await message.answer(text=message_texts.main_menu_clean, reply_markup=ReplyKeyboardRemove())

    keyboard = get_keyboard_by_user_role(user_role)

    await message.answer(text=message_texts.main_menu_answer, reply_markup=keyboard())


@router.callback_query(F.data == callback_texts.main_menu, PrivateChatFilter([private]))
@check_user_registration(get_user_role=True)
async def main_menu_callback_query_handler(callback: CallbackQuery, user_role=None, answer_menu=False):
    keyboard = get_keyboard_by_user_role(user_role)
    text = message_texts.main_menu_answer
    reply_markup = keyboard

    if not answer_menu:
        await callback.message.edit_text(text=text, reply_markup=reply_markup())
    else:
        await callback.message.answer(text=text, reply_markup=reply_markup())

    await callback.answer()
