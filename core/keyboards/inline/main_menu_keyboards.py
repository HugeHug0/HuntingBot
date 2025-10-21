from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.texts import button_texts, callback_texts


def main_menu_hunter_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_texts.profile_register, callback_data=callback_texts.profile_hunter_register)],
        [InlineKeyboardButton(text=button_texts.hunting_request, callback_data=callback_texts.hunting_request)],
        [InlineKeyboardButton(text=button_texts.wh_content, callback_data=callback_texts.wh_content)],
        [InlineKeyboardButton(text=button_texts.settings, callback_data=callback_texts.settings)]
    ])
    return keyboard


def main_menu_hunting_base_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_texts.profile_register, callback_data=callback_texts.profile_hunting_base_register)],
        [InlineKeyboardButton(text=button_texts.wh_content, callback_data=callback_texts.wh_content)],
        [InlineKeyboardButton(text=button_texts.settings, callback_data=callback_texts.settings)]
    ])
    return keyboard


def role_selection_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_texts.hunter_role_select, callback_data=callback_texts.hunter_role_select)],
        [InlineKeyboardButton(text=button_texts.hunting_base_role_select, callback_data=callback_texts.hunting_base_role_select)]
    ])
    return keyboard

