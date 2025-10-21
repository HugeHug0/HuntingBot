from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove

from core.filters.chat_type_filters import PrivateChatFilter, private
from core.handlers.main_menu_handlers import main_menu_handler
from core.texts import message_texts

router = Router()


@router.message(CommandStart(), PrivateChatFilter([private]))
async def start_command_handler(message: Message):
    await message.answer(message_texts.start_command_hello, reply_markup=ReplyKeyboardRemove())
    await main_menu_handler(message)
