from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove

from core.commands import base_commands
from core.filters.chat_type_filters import PrivateChatFilter, private
from core.handlers.main_menu_handlers import main_menu_handler
from core.settings import settings
from core.texts import message_texts

router = Router()

@router.startup()
async def start_bot_handler(bot: Bot):
    await base_commands.set_commands(bot)  # Устанавливаем команды бота в меню

@router.message(CommandStart(), PrivateChatFilter([private]))
async def start_command_handler(message: Message):
    if message.from_user.id in settings.bots.admin_ids:
        await base_commands.set_admin_commands(message.bot)

    await message.answer(message_texts.start_command_hello, reply_markup=ReplyKeyboardRemove())
    await main_menu_handler(message)
