from datetime import datetime

from sqlalchemy import select, delete

from core.db.models import Hunter, HuntingBase, Service
from core.db.postgres import AsyncSessionLocal


from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Union

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
    start_date, end_date = _parse_date_period(data.get("hunting_date"))

    return {
        "tg_id": data["tg_id"],
        "full_name": data["full_name"],
        "phone": data["phone_number"],
        "email": data.get("email"),  # может отсутствовать
        "region": data["region"],
        "hunt_type": data["hunting_type"],
        "start_date": start_date,
        "end_date": end_date,
    }


def _parse_date_period(period_str: str | None):
    """Парсит строку 'yyyy-mm-dd yyyy-mm-dd' → (start_date, end_date)."""
    if not period_str:
        return None, None
    parts = period_str.strip().split()
    if len(parts) != 2:
        return None, None
    start, end = parts
    return _to_date(start), _to_date(end)


def _to_date(date_str: str | None):
    """Преобразует текстовую дату в datetime.date."""
    if not date_str:
        return None
    return datetime.strptime(date_str, "%Y-%m-%d").date()


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
