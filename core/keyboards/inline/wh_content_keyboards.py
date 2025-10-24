from aiogram.types import InlineKeyboardButton

from core.keyboards.inline.general_keyboards import main_menu_inline_keyboard
from core.texts import button_texts, links_texts, callback_texts


def wh_content_main_keyboard():
    buttons = [
        [InlineKeyboardButton(text=button_texts.wh_media_vk, url=links_texts.wh_media_vk_link)],
        [InlineKeyboardButton(text=button_texts.wh_media_youtube, url=links_texts.wh_media_youtube_link)],
        [InlineKeyboardButton(text=button_texts.wh_tg_channel_subscribe, url=links_texts.wh_tg_channel_link)]]
    keyboard = main_menu_inline_keyboard(buttons)
    return keyboard
