from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.keyboards.inline.general_keyboards import main_menu_inline_keyboard
from core.texts import button_texts, callback_texts


def hunt_group_request_inline_keyboard():
    buttons = [[InlineKeyboardButton(text=button_texts.hunt_group_request,
                                     callback_data=callback_texts.hunt_group_request)],
               [InlineKeyboardButton(text=button_texts.hunt_group_answers,
                                     callback_data=callback_texts.hunt_group_answers)]]
    keyboard = main_menu_inline_keyboard(buttons)
    return keyboard


def hunt_group_link_inline_keyboard(forum_link):
    buttons = [[InlineKeyboardButton(text=button_texts.hunt_group_join,
                                     url=forum_link)],
               [InlineKeyboardButton(text=button_texts.hunt_group_answers,
                                     callback_data=callback_texts.hunt_group_answers)]
               ]
    keyboard = main_menu_inline_keyboard(buttons)
    return keyboard


def hunt_group_confirm_request_keyboard():
    buttons = [[InlineKeyboardButton(text=button_texts.confirm_btn,
                                     callback_data=callback_texts.confirm_request)]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
