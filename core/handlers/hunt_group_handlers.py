from aiogram import Router, F
from aiogram.types import CallbackQuery
from pydantic import ValidationError

from core.db_requests.postgres_requests import get_hunt_group_link_or_none, is_request_can_send, send_message_to_group, \
    hunt_group_update_link_and_get_hunter_tg_id, get_admin_messages_for_hunter
from core.filters.chat_type_filters import PrivateChatFilter, private
from core.handlers.main_menu_handlers import main_menu_callback_query_handler
from core.keyboards.inline.general_keyboards import main_menu_inline_keyboard
from core.keyboards.inline.hunt_group_keyboards import hunt_group_link_inline_keyboard, \
    hunt_group_request_inline_keyboard
from core.logging_config import logger
from core.settings import settings
from core.texts import callback_texts, message_texts, button_texts

router = Router()


@router.callback_query(F.data == callback_texts.hunting_request, PrivateChatFilter([private]))
async def hunt_group_handlers(callback: CallbackQuery):
    tg_id = callback.from_user.id
    forum_link = await get_hunt_group_link_or_none(tg_id)

    if forum_link:
        await callback.message.answer(message_texts.hunt_group_join, reply_markup=hunt_group_link_inline_keyboard(forum_link))
    else:
        await callback.message.answer(message_texts.hunt_group_request, reply_markup=hunt_group_request_inline_keyboard())
    await callback.answer()


@router.callback_query(F.data == callback_texts.hunt_group_request)
async def hunt_group_request_callback_query_handler(callback: CallbackQuery):  # Запрос на вступление в форум-группу
    tg = callback.message
    tg_id = tg.from_user.id

    if await is_request_can_send(tg_id=tg_id):
        await callback.answer()

        await send_message_to_group(callback)  # Отправляет заявку в группу для заявок
        await main_menu_callback_query_handler(callback, answer_menu=True)

    else:
        await callback.answer(message_texts.hunting_request_already_sent_to_group)
    await callback.answer()


@router.callback_query(F.data == callback_texts.confirm_request)
async def hunt_group_confirm_callback_query_handler(callback: CallbackQuery):

    msg = callback.message

    msg_id = msg.message_id

    new_forum_link = await callback.bot.create_chat_invite_link(
        chat_id=settings.bots.hunt_group_id,
        expire_date=None,  # бессрочная
        member_limit=1  # одноразовая
    )

    tg_id = await hunt_group_update_link_and_get_hunter_tg_id(msg_id, new_forum_link.invite_link)

    await msg.edit_text(text=msg.text,
                        reply_markup=None)
    await callback.answer(button_texts.request_confirmed)
    if not tg_id:
        return
    try:
        await callback.bot.send_message(chat_id=tg_id,
                                    text=message_texts.hunt_group_confirmed,
                                    reply_markup=main_menu_inline_keyboard())
    except ValidationError as e:
        logger.exception(e)


@router.callback_query(F.data == callback_texts.hunt_group_answers)
async def hunt_group_answers_callback_query_handler(callback: CallbackQuery):
    tg_id = callback.from_user.id
    admin_messages = await get_admin_messages_for_hunter(tg_id)

    if not admin_messages:
        await callback.message.answer(message_texts.no_new_messages, reply_markup=main_menu_inline_keyboard())
        await callback.answer()
        return

    message = '\n\n'.join(admin_messages)

    await callback.message.edit_text(message, reply_markup=main_menu_inline_keyboard())
    await callback.answer()
