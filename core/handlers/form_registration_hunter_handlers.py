from aiogram import Bot, Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from core.services.application_service import ApplicationService
from core.settings import settings

router = Router()


# === FSM ===
class ApplicationForm(StatesGroup):
    full_name = State()
    phone_number = State()
    email = State()
    region = State()
    hunting_type = State()
    hunting_date = State()
    comment = State()
    confirm = State()


# === Клавиатуры ===
def hunting_region_keyboard():
    buttons = [
        [KeyboardButton(text="Север"), KeyboardButton(text="Юг")],
        [KeyboardButton(text="Восток"), KeyboardButton(text="Запад")],
        [KeyboardButton(text="Центр"), KeyboardButton(text=step_back_btn)],
        [KeyboardButton(text=home_btn)],
    ]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)


def hunting_type_keyboard():
    buttons = [
        [KeyboardButton(text="Охота на утку"), KeyboardButton(text="Охота на лося")],
        [KeyboardButton(text="Охота на кабана"), KeyboardButton(text="Охота на зайца")],
        [KeyboardButton(text=step_back_btn)],
        [KeyboardButton(text=home_btn)],
    ]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)


def confirm_keyboard():
    buttons = [
        [KeyboardButton(text="✅ Подтвердить"), KeyboardButton(text="❌ Отмена")],
        [KeyboardButton(text=home_btn)],
    ]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)


# === Старт регистрации ===
@router.message(StateFilter(None), F.text == "🦌 Регистрация охотника")
async def start_registration(message: Message, state: FSMContext):
    answer = message.answer(
        "Введите ваше полное ФИО:",
        reply_markup=start_application_keyboard(),
    )
    await ApplicationService.next(state, ApplicationForm.full_name, answer)


# === ФИО ===
@router.message(ApplicationForm.full_name, F.text)
async def process_full_name(message: Message, state: FSMContext):
    if message.text == home_btn:
        await ApplicationService.back_home(state, message)
        return
    await state.update_data(full_name=message.text.strip())
    answer = message.answer(
        "Введите ваш номер телефона (можно отправить контакт):",
        reply_markup=phone_number_application_keyboard(),
    )
    await ApplicationService.next(state, ApplicationForm.phone_number, answer)


# === Телефон ===
@router.message(ApplicationForm.phone_number)
async def process_phone(message: Message, state: FSMContext):
    if message.text == home_btn:
        await ApplicationService.back_home(state, message)
        return
    elif message.text == step_back_btn:
        await ApplicationService.back(state)
        return

    phone = message.contact.phone_number if message.contact else message.text.strip()
    await state.update_data(phone_number=phone)
    answer = message.answer("Введите ваш E-mail (или нажмите Пропустить):")
    await ApplicationService.next(state, ApplicationForm.email, answer)


# === E-mail ===
@router.message(ApplicationForm.email, F.text)
async def process_email(message: Message, state: FSMContext):
    if message.text == home_btn:
        await ApplicationService.back_home(state, message)
        return
    elif message.text == step_back_btn:
        await ApplicationService.back(state)
        return

    email = None if message.text.lower() == skip_btn.lower() else message.text.strip()
    await state.update_data(email=email)
    answer = message.answer("Выберите регион охоты:", reply_markup=hunting_region_keyboard())
    await ApplicationService.next
