from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.texts import callback_texts, button_texts


def main_menu_inline_keyboard(new_buttons=None, answer_menu=False):
    buttons = []

    if answer_menu:
        menu_btn = [InlineKeyboardButton(text=button_texts.main_menu_btn, callback_data=callback_texts.answer_main_menu)]
    else:
        menu_btn = [InlineKeyboardButton(text=button_texts.main_menu_btn, callback_data=callback_texts.main_menu)]

    if new_buttons:
        buttons.extend(new_buttons)
    buttons.append(menu_btn)

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard

