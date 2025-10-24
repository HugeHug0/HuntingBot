from aiogram import F, Router
from aiogram.types import Message

from core.db_requests.postgres_requests import get_tg_id_by_msg_id_from_request, save_admin_message_for_request
from core.filters.chat_type_filters import PrivateChatFilter, group, supergroup
from core.keyboards.inline.general_keyboards import main_menu_inline_keyboard
from core.logging_config import logger
from core.texts import message_texts

router = Router()


@router.message(F.reply_to_message, PrivateChatFilter([group, supergroup]))
async def admin_reply_handler(message: Message):
    # ID сообщения заявки
    replied_msg_id = message.reply_to_message.message_id

    text = message.text

    tg_id_from_request = await get_tg_id_by_msg_id_from_request(replied_msg_id)
    if tg_id_from_request:
        await save_admin_message_for_request(replied_msg_id, text)

    tg_id = tg_id_from_request
    text = message_texts.admin_reply_on_request_new_message

    if tg_id is None:
        logger.error("tg_id равен None, сообщение не будет отправлено")
        return

    try:
        await message.bot.send_message(chat_id=tg_id,
                                        text=text,
                                        reply_markup=main_menu_inline_keyboard(),
                                       parse_mode=None)
    except Exception as e:
        logger.exception(e)

