import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from core.db.init_db import on_startup
from core.handlers import (start_handlers, main_menu_handlers, role_selection_handlers, hunter_registration_handlers,
                           settings_handlers, hunting_base_registration_handlers, group_reply_handlers,
                           hunt_group_handlers, command_handlers, wh_content_handlers, personal_data_handlers)
from core.settings import settings


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.bots.bot_token, default=DefaultBotProperties(parse_mode='HTML'))
    await bot.delete_webhook(drop_pending_updates=True)


    dp = Dispatcher()
    dp.include_router(command_handlers.router)
    dp.include_router(start_handlers.router)
    dp.include_router(role_selection_handlers.router)
    dp.include_router(personal_data_handlers.router)
    dp.include_router(hunter_registration_handlers.router)
    dp.include_router(hunting_base_registration_handlers.router)
    dp.include_router(group_reply_handlers.router)
    dp.include_router(hunt_group_handlers.router)
    dp.include_router(settings_handlers.router)
    dp.include_router(wh_content_handlers.router)
    dp.include_router(main_menu_handlers.router)

    await on_startup()

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
