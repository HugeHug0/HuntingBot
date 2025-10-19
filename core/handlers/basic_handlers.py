from aiogram import Bot, Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message

from core.keyboards.reply_keyboards import name_application_keyboard, service_application_keyboard, \
    application_keyboard, contact_application_keyboard, phone_number_application_keyboard, \
    start_application_keyboard, file_application_keyboard
from core.services.application_service import ApplicationService
from core.utils import commands, text
from core.settings import settings
from aiogram.fsm.context import FSMContext

from core.utils.fsm_forms import ApplicationForm
from core.utils.text import name_application_message, start_application_btn, service_application_message, \
    details_application_message, file_application_message, contact_application_message, skip_btn, home_btn, \
    step_back_btn, phone_number_btn, username_btn, no_username_message, buttons, is_not_file_message, \
    phone_number_message, invalid_phone_number, final_application_message, confirm_application_btn, next_btn
from core.utils.utils import is_phone_number, final_application_answer, update_files_id

router = Router()

# === События запуска и остановки бота ===
@router.startup()
async def start_bot_handler(bot: Bot):
    await commands.set_commands(bot)  # Устанавливаем команды бота в меню
    await bot.send_message(settings.bots.admin_id, 'Бот запущен')


@router.shutdown()
async def stop_bot_handler(bot: Bot):
    await bot.send_message(settings.bots.admin_id, 'Бот остановлен')


# === Начало заявки ===
@router.message(F.text == start_application_btn)
async def start_application_handler(message: Message, state: FSMContext):
    name = message.from_user.first_name
    surname = message.from_user.last_name
    # Отправляем пользователю сообщение с запросом имени
    answer = message.answer(
        name_application_message,
        reply_markup=name_application_keyboard(f'''{name if name else ''}
{surname if surname else ''}''')
    )

    await ApplicationService.next(state, ApplicationForm.name, answer)  # Сохраняем состояние "name" и ответ для истории


# === Обработка имени пользователя ===
@router.message(ApplicationForm.name, F.text)
async def name_proces_handler(message: Message, state: FSMContext):
    # Ответ для следующего шага — выбор услуги
    answer = message.answer(service_application_message, reply_markup=service_application_keyboard())

    if message.text in (home_btn, step_back_btn):  # Проверяем, нажал ли пользователь "домой" или "назад"
        await ApplicationService.back_home(state, message)
    else:
        await state.update_data(name=message.text)  # Сохраняем имя и переходим к следующему состоянию
        await ApplicationService.next(state, ApplicationForm.service, answer)


# === Выбор услуги ===
@router.message(ApplicationForm.service, F.text)
async def service_proces_handler(message: Message, state: FSMContext):
    # Подготовка ответа для шага с деталями
    answer = message.answer(details_application_message, reply_markup=application_keyboard())

    if message.text == home_btn:
        await ApplicationService.back_home(state, message)
    elif message.text == step_back_btn:
        await ApplicationService.back(state)
    elif message.text in buttons:  # Проверяем, что текст соответствует доступным услугам
        await state.update_data(service=message.text)  # Сохраняем выбранную услугу и переходим к следующему шагу
        await ApplicationService.next(state, ApplicationForm.details, answer)


# === Ввод деталей заявки ===
@router.message(ApplicationForm.details, F.text)
async def details_proces_handler(message: Message, state: FSMContext):
    # Подготовка ответа для шага с файлами
    answer = message.answer(file_application_message, reply_markup=file_application_keyboard())

    if message.text == home_btn:
        await ApplicationService.back_home(state, message)
    elif message.text == step_back_btn:
        await ApplicationService.back(state)
    elif message.text == skip_btn:  # Если пользователь пропускает добавление деталей, переходим к файлам
        await ApplicationService.skip(state, ApplicationForm.files, answer)
    else:
        await state.update_data(details=message.text)  # Сохраняем детали и переходим к следующему состоянию
        await ApplicationService.next(state, ApplicationForm.files, answer)


# === Загрузка файлов пользователем ===
@router.message(ApplicationForm.files)
async def file_proces_handler(message: Message, state: FSMContext):
    # Ответ для следующего шага — выбор контакта
    answer = message.answer(contact_application_message, reply_markup=contact_application_keyboard())

    # Обработка навигации
    if message.text == home_btn:
        await ApplicationService.back_home(state, message)
    elif message.text == step_back_btn:
        await ApplicationService.back(state)
    elif message.text == next_btn:  # Идем дальше
        await ApplicationService.next(state, ApplicationForm.contact, answer)
    elif message.photo or message.document or message.video:
        await update_files_id(message, state)  # Добавляет id файлов
    else:
        await message.answer(is_not_file_message)  # Пользователь отправил не файл


# === Выбор связи по username ===
@router.message(ApplicationForm.contact, F.text == username_btn)
async def username_proces_handler(message: Message, state: FSMContext):
    if not message.from_user.username:
        # Если username нет предупреждаем и сбрасываем состояние
        await message.answer(no_username_message, reply_markup=start_application_keyboard())
        await state.clear()
    else:
        await state.update_data(username=message.from_user.username)  # Сохраняем username
        answer = await final_application_answer(message, state)  # Формируем финальный ответ
        await ApplicationService.next(state, ApplicationForm.confirm, answer, ApplicationForm.username)  # Переходим к подтверждению заявки


# === Выбор связи по номеру телефона ===
@router.message(ApplicationForm.contact, F.text == phone_number_btn)
async def phone_number_common_proces_handler(message: Message, state: FSMContext):
    # Ответ для шага ввода номера телефона
    answer = message.answer(phone_number_message, reply_markup=phone_number_application_keyboard())
    await ApplicationService.next(state, ApplicationForm.phone_number, answer, ApplicationForm.phone_number)


# === Кнопки "домой" и "назад" на контакте ===
@router.message(ApplicationForm.contact)
async def contact_btn_proces_handler(message: Message, state: FSMContext):
    if message.text == home_btn:
        await ApplicationService.back_home(state, message)
    elif message.text == step_back_btn:
        await ApplicationService.back(state)


# === Обработка контакта через Telegram contact ===
@router.message(ApplicationForm.phone_number, F.contact)
async def contact_phone_number_proces_handler(message: Message, state: FSMContext):
    # Получаем номер телефона и сохраняем
    phone_number = message.contact.phone_number
    await state.update_data(phone_number=phone_number)
    answer = await final_application_answer(message, state)  # Отправляем финальный ответ
    await ApplicationService.next(state, ApplicationForm.confirm, answer)


# === Обработка контакта через ввод текста ===
@router.message(ApplicationForm.phone_number, F.text)
async def phone_number_proces_handler(message: Message, state: FSMContext):
    if message.text == home_btn:
        await ApplicationService.back_home(state, message)
    elif message.text == step_back_btn:
        await ApplicationService.back(state)
    else:
        phone_number = message.text.strip()
        if is_phone_number(phone_number):
            await state.update_data(phone_number=phone_number)
            answer = await final_application_answer(message, state)
            await ApplicationService.next(state, ApplicationForm.confirm, answer)
        else:
            # Введён некорректный номер
            await message.answer(invalid_phone_number)


# === Подтверждение заявки ===
@router.message(ApplicationForm.confirm, F.text)
async def confirm_application_handler(message: Message, state: FSMContext):
    if message.text == home_btn:
        await ApplicationService.back_home(state, message)
    elif message.text == step_back_btn:
        await ApplicationService.back(state)
    elif message.text == confirm_application_btn:
        # Сюда можно добавить отправку данных куда-то (CRM, база и т.п.)
        await state.clear()  # Сбрасываем состояние после подтверждения
        await message.answer(final_application_message, reply_markup=start_application_keyboard(), parse_mode='HTML')


@router.message(StateFilter(None))
async def start_application_handler(message: Message):
    await message.answer(text.start_command_message, reply_markup=start_application_keyboard())