from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from core.FSM.registration_fsms import HunterRegistrationFSM
from core.db.postgres import AsyncSessionLocal
from core.db_requests.postgres_requests import get_hunter_by_tg_id, create_hunter_from_state
from core.decorators.register_decorators import check_user_registration
from core.filters.chat_type_filters import PrivateChatFilter, private
from core.handlers.main_menu_handlers import main_menu_handler
from core.keyboards.reply.registration.general_keyboards import home_buttons_keyboard, get_buttons_list_keyboard, \
    confirm_register_keyboard, phone_number_register_keyboard
from core.logging_config import logger
from core.services.question_form_service import QuestionsFormService
from core.settings import settings
from core.texts import callback_texts, message_texts
from core.texts import button_texts
from core.texts.special_names import hunter
from core.utils.utils import is_phone_number, is_valid_email, is_valid_period, send_text_to_group, \
    hunter_format_registration_text, format_comment_text

router = Router()


@router.callback_query(F.data == callback_texts.profile_hunter_register, PrivateChatFilter([private]))
@check_user_registration(filter_user_role=hunter)
async def hunter_registration_handler(callback: CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as session:
        if await get_hunter_by_tg_id(session, callback.from_user.id):
            await callback.answer(message_texts.user_already_registered)
            return
    await callback.answer()

    await callback.message.answer(message_texts.start_hunter_registration, reply_markup=ReplyKeyboardRemove())

    answer = callback.message.answer(
        message_texts.hunter_registration_name,
        reply_markup=home_buttons_keyboard(back_home=True)
    )

    await QuestionsFormService.next(state, HunterRegistrationFSM.full_name, answer)  # Сохраняем состояние и ответ для истории


# === Обработка имени пользователя ===
@router.message(HunterRegistrationFSM.full_name, F.text)
async def hunter_name_proces_handler(message: Message, state: FSMContext):
    # Ответ для шага ввода номера телефона
    answer = message.answer(message_texts.hunter_registration_phone_number,
                            reply_markup=phone_number_register_keyboard())

    if message.text in button_texts.home_btn:
        await state.clear()
        await main_menu_handler(message)

    else:
        await state.update_data(full_name=message.text)  # Сохраняем имя и переходим к следующему состоянию
        await QuestionsFormService.next(state, HunterRegistrationFSM.phone_number, answer)


# === Обработка контакта через Telegram contact ===
@router.message(HunterRegistrationFSM.phone_number, F.contact)
async def hunter_contact_phone_number_process_handler(message: Message, state: FSMContext):
    # Ответ для шага ввода email
    answer = message.answer(message_texts.hunter_registration_email,
                            reply_markup=home_buttons_keyboard(skip=True, back=True, back_home=True))

    # Получаем номер телефона и сохраняем
    phone_number = message.contact.phone_number
    await state.update_data(phone_number=phone_number)
    await QuestionsFormService.next(state, HunterRegistrationFSM.email, answer)


# === Обработка контакта через ввод текста ===
@router.message(HunterRegistrationFSM.phone_number, F.text)
async def hunter_phone_number_process_handler(message: Message, state: FSMContext):
    if message.text == button_texts.home_btn:
        await state.clear()
        await main_menu_handler(message)
    elif message.text == button_texts.step_back_btn:
        await QuestionsFormService.back(state)
    else:
        phone_number = message.text.strip()
        if is_phone_number(phone_number):
            await state.update_data(phone_number=phone_number)
            answer = message.answer(message_texts.hunter_registration_email,
                            reply_markup=home_buttons_keyboard(skip=True, back=True, back_home=True))
            await QuestionsFormService.next(state, HunterRegistrationFSM.email, answer)
        else:
            # Введён некорректный номер
            await message.answer(message_texts.invalid_phone_number)


# === Обработка email ===
@router.message(HunterRegistrationFSM.email, F.text)
async def hunter_email_process_handler(message: Message, state: FSMContext):
    # Ответ для шага ввода региона
    answer = message.answer(message_texts.hunter_registration_region,
                            reply_markup=get_buttons_list_keyboard(button_texts.regions_list))

    if message.text == button_texts.home_btn:
        await state.clear()
        await main_menu_handler(message)
    elif message.text == button_texts.step_back_btn:
        await QuestionsFormService.back(state)
    elif message.text == button_texts.skip_btn:
        await QuestionsFormService.skip(state, HunterRegistrationFSM.region, answer)
    else:
        email = message.text
        if is_valid_email(email):
            await state.update_data(email=email)
            await QuestionsFormService.next(state, HunterRegistrationFSM.region, answer)
        else:
            await message.answer(message_texts.invalid_email)


# === Обработка region ===
@router.message(HunterRegistrationFSM.region, F.text)
async def hunter_region_process_handler(message: Message, state: FSMContext):
    # Ответ для шага ввода вида охоты
    answer = message.answer(message_texts.hunter_registration_hunting_type,
                            reply_markup=get_buttons_list_keyboard(button_texts.hunting_types_list))

    if message.text == button_texts.home_btn:
        await state.clear()
        await main_menu_handler(message)
    elif message.text == button_texts.step_back_btn:
        await QuestionsFormService.back(state)
    else:
        await state.update_data(region=message.text)  # Сохраняем выбранную услугу и переходим к следующему шагу
        await QuestionsFormService.next(state, HunterRegistrationFSM.hunting_type, answer)


# === Обработка hunt_type ===
@router.message(HunterRegistrationFSM.hunting_type, F.text)
async def hunter_hunting_type_process_handler(message: Message, state: FSMContext):
    # Ответ для шага ввода вида охоты
    answer = message.answer(message_texts.hunter_registration_hunting_date,
                            reply_markup=home_buttons_keyboard(back=True, back_home=True))

    if message.text == button_texts.home_btn:
        await state.clear()
        await main_menu_handler(message)
    elif message.text == button_texts.step_back_btn:
        await QuestionsFormService.back(state)
    else:
        await state.update_data(hunting_type=message.text)  # Сохраняем выбранную услугу и переходим к следующему шагу
        await QuestionsFormService.next(state, HunterRegistrationFSM.hunting_date, answer)


# === Обработка hunting_date ===
@router.message(HunterRegistrationFSM.hunting_date, F.text)
async def hunter_hunting_date_process_handler(message: Message, state: FSMContext):
    # Ответ для шага ввода периода
    answer = message.answer(message_texts.hunter_registration_comment,
                            reply_markup=home_buttons_keyboard(skip=True, back=True, back_home=True))

    if message.text == button_texts.home_btn:
        await state.clear()
        await main_menu_handler(message)
    elif message.text == button_texts.step_back_btn:
        await QuestionsFormService.back(state)
    else:
        period = message.text
        if is_valid_period(period):
            await state.update_data(hunting_date=period)
            await QuestionsFormService.next(state, HunterRegistrationFSM.comment, answer)
        else:
            await message.answer(message_texts.invalid_date)


# === Обработка комментария ===
@router.message(HunterRegistrationFSM.comment, F.text)
async def hunter_comment_process_handler(message: Message, state: FSMContext):
    # Ответ для шага комментария

    if message.text == button_texts.home_btn:
        await state.clear()
        await main_menu_handler(message)
    elif message.text == button_texts.step_back_btn:
        await QuestionsFormService.back(state)
    elif message.text == button_texts.skip_btn:
        answer = message.answer(await hunter_format_registration_text(state),
                                reply_markup=confirm_register_keyboard())
        await QuestionsFormService.skip(state, HunterRegistrationFSM.confirm, answer)
    else:
        text = message.text[:4096]

        await state.update_data(comment=text)

        answer = message.answer(await hunter_format_registration_text(state),
                                reply_markup=confirm_register_keyboard())
        await QuestionsFormService.next(state, HunterRegistrationFSM.confirm, answer)



# === Подтверждение заявки ===
@router.message(HunterRegistrationFSM.confirm, F.text)
async def confirm_application_handler(message: Message, state: FSMContext):
    if message.text == button_texts.home_btn:
        await state.clear()
        await main_menu_handler(message)
    elif message.text == button_texts.step_back_btn:
        await QuestionsFormService.back(state)
    elif message.text == button_texts.confirm_btn:
        await state.update_data(tg_id=message.from_user.id)

        async with AsyncSessionLocal() as session:
            try:
                await create_hunter_from_state(state, session)  # Сохраняет в бд
                await message.answer(message_texts.successful_registration)
                format_text = await format_comment_text(state, message.from_user.id)
                await send_text_to_group(message.bot, settings.bots.request_group_id, format_text)
            except Exception as e:
                await session.rollback()
                logger.error(f'error: {e}')
                await message.answer(message_texts.error_registration)


        await state.clear()  # Сбрасывает состояние после подтверждения
        await main_menu_handler(message)
