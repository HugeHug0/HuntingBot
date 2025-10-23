from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from core.FSM.registration_fsms import HuntingBaseRegistrationFSM
from core.db.postgres import AsyncSessionLocal
from core.db_requests.postgres_requests import get_hunting_base_by_tg_id, create_hunting_base_from_state
from core.decorators.register_decorators import check_user_registration
from core.filters.chat_type_filters import PrivateChatFilter, private
from core.handlers.main_menu_handlers import main_menu_handler
from core.keyboards.reply.registration.general_keyboards import (
    home_buttons_keyboard, get_buttons_list_keyboard, phone_number_register_keyboard, confirm_register_keyboard)
from core.logging_config import logger

from core.services.question_form_service import QuestionsFormService
from core.texts import callback_texts, message_texts, button_texts
from core.texts.special_names import hunting_base
from core.utils.utils import get_format_services_selected, get_services_selected, \
    is_phone_number, hunting_base_format_registration_text


router = Router()


# === Старт регистрации базы ===
@router.callback_query(F.data == callback_texts.profile_hunting_base_register, PrivateChatFilter([private]))
@check_user_registration(filter_user_role=hunting_base)
async def hunting_base_registration_handler(callback: CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as session:
        if await get_hunting_base_by_tg_id(session, callback.from_user.id):
            await callback.answer(message_texts.user_already_registered)
            return

    await callback.answer()

    await callback.message.answer(message_texts.start_hunting_base_registration, reply_markup=ReplyKeyboardRemove())

    answer = callback.message.answer(
        message_texts.hunting_base_registration_name,
        reply_markup=home_buttons_keyboard(back_home=True)
    )

    await QuestionsFormService.next(state, HuntingBaseRegistrationFSM.name, answer)


# === Название базы / охотхозяйства ===
@router.message(HuntingBaseRegistrationFSM.name, F.text)
async def hunting_base_name_process_handler(message: Message, state: FSMContext):
    if message.text == button_texts.home_btn:
        await state.clear()
        await main_menu_handler(message)
        return

    await state.update_data(name=message.text)
    answer = message.answer(
        message_texts.hunting_base_registration_region,
        reply_markup=get_buttons_list_keyboard(button_texts.regions_list)
    )
    await QuestionsFormService.next(state, HuntingBaseRegistrationFSM.region, answer)


# === Регион ===
@router.message(HuntingBaseRegistrationFSM.region, F.text)
async def hunting_base_region_process_handler(message: Message, state: FSMContext):
    if message.text == button_texts.home_btn:
        await state.clear()
        await main_menu_handler(message)
        return
    elif message.text == button_texts.step_back_btn:
        await QuestionsFormService.back(state)
        return
    elif message.text in button_texts.regions_list:
        await state.update_data(region=message.text)
        answer = message.answer(
            message_texts.hunting_base_registration_services,
            reply_markup=get_buttons_list_keyboard(button_texts.hunting_types_list, skip=True)
        )
        await QuestionsFormService.next(state, HuntingBaseRegistrationFSM.services, answer)


# === Виды услуг ===
@router.message(HuntingBaseRegistrationFSM.services, F.text)
async def hunting_base_services_process_handler(message: Message, state: FSMContext):
    answer = message.answer(
        message_texts.hunting_base_registration_contact_person,
        reply_markup=home_buttons_keyboard(back_home=True, back=True)
    )
    if message.text == button_texts.home_btn:
        await state.clear()
        await main_menu_handler(message)
    elif message.text == button_texts.step_back_btn:
        await QuestionsFormService.back(state)
    elif message.text == button_texts.next_btn:
        data = await state.get_data()
        selected = data.get("services", [])
        if selected:
            await QuestionsFormService.next(state, HuntingBaseRegistrationFSM.contact_person, answer)
        else:
            await message.answer(message_texts.no_services_selected)
    elif message.text in button_texts.hunting_types_list:
        key = message.text
        selected = await get_services_selected(state, key)

        await state.update_data(services=list(selected))
        await message.answer(get_format_services_selected(selected))


# === contact person ===
@router.message(HuntingBaseRegistrationFSM.contact_person, F.text)
async def hunting_base_contact_person_process_handler(message: Message, state: FSMContext):
    if message.text == button_texts.home_btn:
        await state.clear()
        await main_menu_handler(message)
        return
    elif message.text == button_texts.step_back_btn:
        await QuestionsFormService.back(state)
        return

    text = message.text.strip()
    await state.update_data(contact_person=text)
    answer = message.answer(
        message_texts.hunting_base_registration_contact,
        reply_markup=phone_number_register_keyboard()
    )
    await QuestionsFormService.next(state, HuntingBaseRegistrationFSM.contact, answer)


# === Обработка контакта через Telegram contact ===
@router.message(HuntingBaseRegistrationFSM.contact, F.contact)
async def hunting_base_contact_phone_number_process_handler(message: Message, state: FSMContext):
    # Ответ для шага ввода website
    answer = message.answer(message_texts.hunting_base_registration_website,
                            reply_markup=home_buttons_keyboard(skip=True, back=True, back_home=True))

    # Получаем номер телефона и сохраняем
    phone_number = message.contact.phone_number
    await state.update_data(contact=phone_number)
    await QuestionsFormService.next(state, HuntingBaseRegistrationFSM.website, answer)


# === Обработка контакта через ввод текста ===
@router.message(HuntingBaseRegistrationFSM.contact, F.text)
async def hunting_base_phone_number_process_handler(message: Message, state: FSMContext):
    if message.text == button_texts.home_btn:
        await state.clear()
        await main_menu_handler(message)
    elif message.text == button_texts.step_back_btn:
        await QuestionsFormService.back(state)
    else:
        phone_number = message.text.strip()
        if is_phone_number(phone_number):
            await state.update_data(contact=phone_number)
            answer = message.answer(message_texts.hunting_base_registration_website,
                            reply_markup=home_buttons_keyboard(skip=True, back=True, back_home=True))
            await QuestionsFormService.next(state, HuntingBaseRegistrationFSM.website, answer)
        else:
            # Введён некорректный номер
            await message.answer(message_texts.invalid_phone_number)


# === Сайт / соцсети ===
@router.message(HuntingBaseRegistrationFSM.website, F.text)
async def hunting_base_website_process_handler(message: Message, state: FSMContext):


    if message.text == button_texts.home_btn:
        await state.clear()
        await main_menu_handler(message)
        return
    elif message.text == button_texts.step_back_btn:
        await QuestionsFormService.back(state)
        return
    elif message.text == button_texts.skip_btn:
        answer = message.answer(await hunting_base_format_registration_text(state),
                                reply_markup=confirm_register_keyboard()
                                )
        await QuestionsFormService.skip(state, HuntingBaseRegistrationFSM.confirm, answer)
        return

    await state.update_data(website=message.text)
    answer = message.answer(await hunting_base_format_registration_text(state),
                            reply_markup=confirm_register_keyboard()
                            )
    await QuestionsFormService.next(state, HuntingBaseRegistrationFSM.confirm, answer)


# === Подтверждение заявки ===
@router.message(HuntingBaseRegistrationFSM.confirm, F.text)
async def hunting_base_confirm_process_handler(message: Message, state: FSMContext):
    if message.text == button_texts.home_btn:
        await state.clear()
        await main_menu_handler(message)
        return
    elif message.text == button_texts.step_back_btn:
        await QuestionsFormService.back(state)
        return
    elif message.text == button_texts.confirm_btn:
        await state.update_data(tg_id=message.from_user.id)

        async with AsyncSessionLocal() as session:
            try:
                await create_hunting_base_from_state(state, session)  # Сохраняет в бд
                await message.answer(message_texts.successful_registration)
            except Exception as e:
                await session.rollback()
                logger.error(f'error: {e}')
                await message.answer(message_texts.error_registration)

        await state.clear()
        await main_menu_handler(message)
