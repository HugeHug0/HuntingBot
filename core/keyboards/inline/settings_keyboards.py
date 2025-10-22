from aiogram.types import InlineKeyboardButton

from core.keyboards.inline.general_keyboards import main_menu_inline_keyboard
from core.texts import button_texts, callback_texts


def main_settings_keyboard():
    buttons = [[InlineKeyboardButton(text=button_texts.log_out, callback_data=callback_texts.log_out)]]
    keyboard = main_menu_inline_keyboard(buttons)
    return keyboard
