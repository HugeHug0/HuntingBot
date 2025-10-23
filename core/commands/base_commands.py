from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from aiogram import Bot

from core.logging_config import logger
from core.settings import settings


# имена команд
command_name_hunters_with_link = "hunters_with_link"
command_name_get_all_hunters = "get_all_hunters"
command_name_delete_hunter = "delete_hunter"
command_name_get_all_hunting_bases = "get_all_hunting_bases"
command_name_delete_hunting_base = "delete_hunting_base"
command_name_delete_request = "delete_request"
command_name_help_commands = "help_commands"

# команды для всех пользователей
common_commands = [
    BotCommand(
        command='start',
        description='Начало работы с ботом'
    )
]

# команды для администраторов
admin_commands = common_commands + [
    BotCommand(
        command=command_name_help_commands,
        description='Инструкция по использованию команд для админов'
    ),
    BotCommand(
        command=command_name_get_all_hunters,
        description='Вывод всех зарегистрированных охотников'
    ),
    BotCommand(
        command=command_name_hunters_with_link,
        description='Вывод всех охотников с доступом к охотничьей группе'
    ),
    BotCommand(
        command=command_name_get_all_hunting_bases,
        description='Вывод всех охотничьих баз'
    ),
    BotCommand(
        command=command_name_delete_hunter,
        description='Удалить охотника по <tg_id>'
    ),
    BotCommand(
        command=command_name_delete_hunting_base,
        description='Удалить охотничью базу по <tg_id>'
    ),
    BotCommand(
        command=command_name_delete_request,
        description='Удалить заявку охотника по <tg_id>'
    )
]

async def set_commands(bot: Bot):
    # команды для всех
    await bot.set_my_commands(common_commands, scope=BotCommandScopeDefault())

async def set_admin_commands(bot: Bot):
    # команды только для админов
    for admin_id in settings.bots.admin_ids:
        try:
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=int(admin_id)))
        except TelegramBadRequest:
            logger.info(f'Не удалось установить команды для admin_id {admin_id}')

