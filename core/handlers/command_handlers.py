from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.commands.base_commands import command_name_hunters_with_link, command_name_get_all_hunters, \
    command_name_get_all_hunting_bases, command_name_delete_hunter, command_name_delete_hunting_base, \
    command_name_delete_request, command_name_help_commands
from core.db_requests.command_postgres_requests import get_hunters_with_link, get_all_hunters, \
    delete_hunter_by_tg_id_and_get_text, handle_delete_request_command, get_all_hunting_bases, \
    delete_hunting_base_by_tg_id_and_get_text
from core.filters.admin_filters import AdminFilter
from core.filters.chat_type_filters import PrivateChatFilter, private
from core.keyboards.inline.general_keyboards import main_menu_inline_keyboard


HELP_COMMAND_TEXT = """Команды для всех:
/start — начало работы с ботом. Показывает приветствие и основное меню.

Команды для администраторов:
/get_all_hunters — Список всех зарегистрированных в базе охотников
/hunters_with_link — Список всех зарегистрированных охотников с доступом к охотничьей группе
/get_all_hunting_bases — Список всех охотничьих баз
/delete_hunter <tg_id> — Удалить охотника по его Telegram ID. tg_id можно узнать из команды /get_all_hunters
/delete_hunting_base <tg_id> — Удалить охотничью базу по её Telegram ID. tg_id можно узнать из команды /get_all_hunting_bases
/delete_request <tg_id> — Удалить заявку охотника на охоту по его Telegram ID
"""


router = Router()


@router.message(Command(command_name_hunters_with_link), PrivateChatFilter([private]), AdminFilter())
async def get_hunters_with_link_command(message: Message):
    hunters_with_link_list_text = await get_hunters_with_link()

    await message.answer(text=hunters_with_link_list_text, reply_markup=main_menu_inline_keyboard(), parse_mode=None)

@router.message(Command(command_name_get_all_hunters), PrivateChatFilter([private]), AdminFilter())
async def get_all_hunters_command(message: Message):
    hunters_link_list_text = await get_all_hunters()

    await message.answer(hunters_link_list_text, reply_markup=main_menu_inline_keyboard(), parse_mode=None)

@router.message(Command(command_name_get_all_hunting_bases), PrivateChatFilter([private]), AdminFilter())
async def get_all_hunting_bases_command(message: Message):
    hunting_bases_link_list_text = await get_all_hunting_bases()

    await message.answer(hunting_bases_link_list_text, reply_markup=main_menu_inline_keyboard(), parse_mode=None)

@router.message(Command(command_name_delete_hunter), PrivateChatFilter([private]), AdminFilter())
async def delete_hunter_by_chat_id_command(message: Message):
    raw_text = message.text
    delete_hunter_text = await delete_hunter_by_tg_id_and_get_text(raw_text)
    await message.answer(delete_hunter_text, reply_markup = main_menu_inline_keyboard(), parse_mode=None)

@router.message(Command(command_name_delete_hunting_base), PrivateChatFilter([private]), AdminFilter())
async def delete_hunting_base_by_chat_id_command(message: Message):
    raw_text = message.text
    delete_hunter_text = await delete_hunting_base_by_tg_id_and_get_text(raw_text)
    await message.answer(delete_hunter_text, reply_markup = main_menu_inline_keyboard(), parse_mode=None)

@router.message(Command(command_name_delete_request), PrivateChatFilter([private]), AdminFilter())
async def delete_request_command(message: Message):
    text_raw = message.text
    delete_request_text = await handle_delete_request_command(text_raw)
    await message.answer(delete_request_text, reply_markup=main_menu_inline_keyboard(), parse_mode=None)

@router.message(Command(command_name_help_commands), PrivateChatFilter([private]), AdminFilter())
async def help_commands_command(message: Message):
    text = HELP_COMMAND_TEXT
    await message.answer(text, reply_markup=main_menu_inline_keyboard(), parse_mode=None)
