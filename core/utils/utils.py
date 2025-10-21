from core.keyboards.inline.main_menu_keyboards import main_menu_hunting_base_keyboard, main_menu_hunter_keyboard
from core.texts.special_names import hunting_base, hunter


def get_keyboard_by_user_role(user_role):
    if user_role == hunter:
        return main_menu_hunter_keyboard
    elif user_role == hunting_base:
        return main_menu_hunting_base_keyboard
