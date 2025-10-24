from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from core.texts import button_texts


def home_buttons_keyboard(skip=False, back=False, back_home=False, extend_buttons=None):
    skip_btn = [KeyboardButton(text=button_texts.skip_btn)]
    back_btn = [KeyboardButton(text=button_texts.step_back_btn)]
    home_btn = [KeyboardButton(text=button_texts.home_btn)]

    buttons = []

    if extend_buttons:
        buttons.extend(extend_buttons)

    if skip:
        buttons.append(skip_btn)
    if back:
        buttons.append(back_btn)
    if back_home:
        buttons.append(home_btn)

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def get_buttons_list_keyboard(buttons, skip=False):
    builder = ReplyKeyboardBuilder()
    if skip:
        builder.row(KeyboardButton(text=button_texts.next_btn), width=3)
    builder.add(*[KeyboardButton(text=button) for button in buttons])
    builder.adjust(3)

    builder.row(KeyboardButton(text=button_texts.step_back_btn),
                KeyboardButton(text=button_texts.home_btn))

    kb = builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    return kb

def confirm_register_keyboard():
    buttons = [[KeyboardButton(text=button_texts.confirm_btn)]]
    keyboard = home_buttons_keyboard(back=True, back_home=True, extend_buttons=buttons)
    return keyboard

def phone_number_register_keyboard():
    buttons = [[KeyboardButton(text=button_texts.share_phone_number_btn, request_contact=True)]]
    keyboard = home_buttons_keyboard(back=True, back_home=True, extend_buttons=buttons)
    return keyboard
