from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from core.filters.chat_type_filters import PrivateChatFilter, private
from core.texts import message_texts

router = Router()


@router.message(CommandStart(), PrivateChatFilter([private]))
async def main_menu_handler(message: Message):
    await message.answer(text=message_texts.main_menu_message, )
