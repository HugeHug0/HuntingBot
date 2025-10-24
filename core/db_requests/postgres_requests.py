from datetime import datetime

from aiogram.types import CallbackQuery
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from core.db.models import Hunter, HuntingBase, Service, Request, AdminMessage
from core.db.postgres import AsyncSessionLocal


from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Union

from core.keyboards.inline.hunt_group_keyboards import hunt_group_confirm_request_keyboard
from core.logging_config import logger
from core.settings import settings
from core.texts import message_texts
from core.texts.special_names import hunter, hunting_base


async def get_hunter_by_tg_id(session: AsyncSession, tg_id: int) -> Optional[Hunter]:
    """Возвращает Hunter по Telegram ID."""
    result = await session.execute(select(Hunter).where(Hunter.tg_id == tg_id))
    return result.scalar_one_or_none()


async def get_hunting_base_by_tg_id(session: AsyncSession, tg_id: int) -> Optional[HuntingBase]:
    """Возвращает HuntingBase по Telegram ID."""
    result = await session.execute(select(HuntingBase).where(HuntingBase.tg_id == tg_id))
    return result.scalar_one_or_none()


async def delete_hunter_and_base(session: AsyncSession, tg_id: int) -> None:
    """Удаляет Hunter и HuntingBase по Telegram ID."""
    await session.execute(delete(Hunter).where(Hunter.tg_id == tg_id))
    await session.execute(delete(HuntingBase).where(HuntingBase.tg_id == tg_id))
    await session.commit()


async def get_or_clear_hunter_records(tg_id: int) -> Optional[Union[Hunter, HuntingBase]]:
    """
    Проверяет наличие записей Hunter и HuntingBase по Telegram ID.
    Если обе есть — удаляет обе.
    Если одна есть — возвращает её.
    Если нет ни одной — возвращает None.
    """
    async with AsyncSessionLocal() as session:
        hunter_obj = await get_hunter_by_tg_id(session, tg_id)
        hunting_base_obj = await get_hunting_base_by_tg_id(session, tg_id)

        if hunter_obj and hunting_base_obj:
            await delete_hunter_and_base(session, tg_id)
            return None

        if hunter_obj:
            return hunter
        elif hunting_base_obj:
            return hunting_base

async def create_hunter_from_state(state, session: AsyncSession) -> Hunter:
    """Создаёт запись Hunter из FSM state."""

    data = await state.get_data()

    parsed_data = _parse_state_data(data)
    hunter_obj = _build_hunter(parsed_data)

    session.add(hunter_obj)
    await session.commit()
    return hunter_obj


def _parse_state_data(data: dict) -> dict:
    """Подготавливает данные из FSM state к сохранению."""

    return {
        "tg_id": data["tg_id"],
        "full_name": data["full_name"],
        "phone": data["phone_number"],
        "email": data.get("email"),
        "region": data["region"],
        "hunt_type": data["hunting_type"],
    }


# def _parse_date_period(period_str: str | None):
#     """Парсит строку 'yyyy-mm-dd yyyy-mm-dd' → (start_date, end_date)."""
#     if not period_str:
#         return None, None
#     parts = period_str.strip().split()
#     if len(parts) != 2:
#         return None, None
#     start, end = parts
#     return _to_date(start), _to_date(end)


# def _to_date(date_str: str | None):
#     """Преобразует текстовую дату в datetime.date."""
#     if not date_str:
#         return None
#     return datetime.strptime(date_str, "%Y-%m-%d").date()


def _build_hunter(data: dict) -> Hunter:
    """Создаёт объект модели Hunter из данных."""
    return Hunter(**data)


async def create_hunting_base_from_state(state, session: AsyncSession) -> HuntingBase:
    """Создаёт запись HuntingBase и привязывает услуги."""
    data = await state.get_data()
    service_names = data.get("services", [])

    base = _build_hunting_base(data)
    base.services = await _get_or_create_services(service_names, session)

    session.add(base)
    await session.commit()
    return base


def _build_hunting_base(data: dict) -> HuntingBase:
    """Создаёт объект охотничьей базы из данных state."""
    return HuntingBase(
        tg_id=data["tg_id"],
        name=data["name"],
        region=data["region"],
        contact_person=data["contact_person"],
        contact=data["contact"],
        website=data.get("website"),
    )


async def _get_or_create_services(names: list[str], session: AsyncSession) -> list[Service]:
    """Возвращает существующие или создаёт новые услуги по списку."""
    services = []
    for name in names:
        result = await session.execute(select(Service).where(Service.name == name))
        service = result.scalars().first()
        if not service:
            service = Service(name=name)
            session.add(service)
        services.append(service)
    return services

async def get_hunt_group_link_or_none(tg_id: int) -> str | None:
    """Возвращает hunting_link по tg_id охотника, если существует."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Request.hunting_link)
            .join(Hunter)
            .where(Hunter.tg_id == tg_id)
        )
        return result.scalar_one_or_none()

async def is_request_can_send(tg_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Hunter)
            .where(Hunter.tg_id == tg_id)
            .options(selectinload(Hunter.request))
        )
        hunter_obj = result.scalar_one_or_none()
        if not hunter_obj:
            return False
        return hunter_obj.request is None


async def get_hunter_with_request(session, tg_id: int) -> Hunter | None:
    """Возвращает охотника вместе с его заявкой."""
    result = await session.execute(
        select(Hunter)
        .where(Hunter.tg_id == tg_id)
        .options(selectinload(Hunter.request))
    )
    return result.scalar_one_or_none()


async def build_request_message(hunter_obj: Hunter) -> str:
    """Формирует текст заявки для отправки в группу."""
    return (
        f"📩 Заявка от охотника\n"
        f"👤 Имя: {hunter_obj.full_name or '—'}\n"
        f"📞 Телефон: {hunter_obj.phone or '—'}\n"
        f"📧 Email: {hunter_obj.email or '—'}\n"
        f"📍 Регион: {hunter_obj.region or '—'}\n"
        f"🏹 Тип охоты: {hunter_obj.hunt_type or '—'}\n"
        f"🆔 Telegram ID: {hunter_obj.tg_id}"
    )


async def send_message_to_group(callback: CallbackQuery):
    """Отправляет заявку охотника в группу Telegram."""
    tg_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        hunter_obj = await get_hunter_with_request(session, tg_id)
        if not hunter_obj:
            await callback.answer(message_texts.unregister_hunter)
            return

        message_text = await build_request_message(hunter_obj)

        try:
            msg = await callback.bot.send_message(
                chat_id=settings.bots.request_group_id,
                text=message_text,
                reply_markup=hunt_group_confirm_request_keyboard()
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке заявки в группу: {e}")
            await callback.message.answer(message_texts.invalid_send_to_group)
            return

        # если заявка уже есть — обновляем сообщение
        if hunter_obj.request:
            hunter_obj.request.tg_message_id = msg.message_id
        else:
            new_request = Request(
                hunter_id=hunter_obj.id,
                tg_message_id=msg.message_id,
            )
            session.add(new_request)

        await session.commit()
        await callback.message.answer(message_texts.successful_send_to_group)


async def get_request_object_with_hunter_by_msg_id(session, msg_id: int):
    """Возвращает Request по tg_message_id вместе с охотником."""
    result = await session.execute(
        select(Request)
        .options(selectinload(Request.hunter))
        .where(Request.tg_message_id == msg_id)
    )
    return result.scalar_one_or_none()

async def hunt_group_update_link_and_get_hunter_tg_id(msg_id, new_hunt_group_link):
    async with AsyncSessionLocal() as session:
        request_obj = await get_request_object_with_hunter_by_msg_id(session, msg_id)

        if not request_obj:
            return False

        await update_request_group_link(request_obj, new_hunt_group_link)

        session.add(request_obj)
        await session.commit()
        return request_obj.hunter.tg_id

async def update_request_group_link(request_obj, new_hunt_group_link):
    if request_obj:
        request_obj.hunting_link = new_hunt_group_link

async def get_admin_messages_for_hunter(tg_id: int) -> list[str]:
    """Возвращает список текстов ответов админов по tg_id охотника."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Hunter)
            .where(Hunter.tg_id == tg_id)
            .options(
                selectinload(Hunter.request).selectinload(Request.admin_messages)
            )
        )
        hunter_obj = result.scalar_one_or_none()

        if not hunter_obj or not hunter_obj.request:
            return []

        return [msg.message_text for msg in hunter_obj.request.admin_messages]


async def get_tg_id_by_msg_id_from_request(msg_id):
    async with AsyncSessionLocal() as session:
        request_obj = await get_request_object_with_hunter_by_msg_id(session, msg_id)
        if request_obj:
            return request_obj.hunter.tg_id

async def save_admin_message_for_request(replied_msg_id, text):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Request).where(Request.tg_message_id == replied_msg_id)
        )
        request_obj = result.scalar_one_or_none()
        if not request_obj:
            return  # заявка не найдена

        admin_response = AdminMessage(
            request_id=request_obj.id,
            message_text=text
        )
        session.add(admin_response)
        await session.commit()

