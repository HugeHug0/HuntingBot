from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.texts import button_texts, callback_texts, links_texts
from core.texts.special_names import hunter


def get_personal_data_before_registration_keyboard_by_role(user_role):
    if user_role == hunter:
        register_button = [InlineKeyboardButton(text=button_texts.agree_to_processing_data,
                                                callback_data=callback_texts.profile_hunter_register)]
    else:
        register_button = [InlineKeyboardButton(text=button_texts.agree_to_processing_data,
                                                callback_data=callback_texts.profile_hunting_base_register)]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text=button_texts.personal_data_about,
                                                        url=links_texts.personal_data_link)],
                                    register_button,
                                    [InlineKeyboardButton(text=button_texts.dont_agree_processing_data,
                                                        callback_data=callback_texts.main_menu)]])

    return keyboard
