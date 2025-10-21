from sqlalchemy import select, delete

from core.db.models import Hunter, HuntingBase
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
