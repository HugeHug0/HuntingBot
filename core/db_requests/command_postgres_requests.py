from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.db.models import Hunter, Request, HuntingBase
from core.db.postgres import AsyncSessionLocal


# ========= Вернуть всех охотников с hunting_link =========
async def _build_query():
    return (
        select(Hunter)
        .options(selectinload(Hunter.request))
        .where(Hunter.request.has(Request.hunting_link.isnot(None)))
    )


async def _fetch_hunters(session: AsyncSession):
    stmt = await _build_query()
    res = await session.scalars(stmt)
    return res.all()


def _format_hunter_with_link(h, i):
    r = h.request
    return (
        f"{i}. {h.full_name}\n"
        f"   Telegram ID: {h.tg_id}\n"
        f"   Phone: {h.phone}\n"
        f"   Email: {h.email or '—'}\n"
        f"   Hunting link: {r.hunting_link if r else '—'}\n\n"
    )


async def get_hunters_with_link():
    async with AsyncSessionLocal() as session:
        hunters = await _fetch_hunters(session)
        if not hunters:
            return "📋 Нет охотников с hunting_link."
        lines = ["📋 Список охотников с hunting_link:\n"]
        for i, h in enumerate(hunters, 1):
            lines.append(_format_hunter_with_link(h, i))
        return "\n".join(lines).strip()


# ========= Вернуть всех охотников полностью =========
async def _build_query_all():
    return select(Hunter)


async def _fetch_all_hunters(session: AsyncSession):
    stmt = await _build_query_all()
    res = await session.scalars(stmt)
    return res.all()


def _format_hunter_all(h, i):
    return (
        f"{i}. {h.full_name}\n"
        f"   Telegram ID: {h.tg_id}\n"
        f"   Phone: {h.phone}\n"
        f"   Email: {h.email or '—'}\n"
        f"   Region: {h.region}\n"
        f"   Hunt type: {h.hunt_type}\n"
        f"   Start date: {h.start_date}\n"
        f"   End date: {h.end_date}\n\n"
    )


async def get_all_hunters():
    async with AsyncSessionLocal() as session:
        hunters = await _fetch_all_hunters(session)
        if not hunters:
            return "📋 Нет зарегистрированных охотников."
        lines = ["📋 Полный список охотников:\n"]
        for i, h in enumerate(hunters, 1):
            lines.append(_format_hunter_all(h, i))
        return "\n".join(lines).strip()


# ========= Удаление охотника по tg_id =========
async def _parse_tg_id(text: str) -> int | str:
    parts = text.split()
    if len(parts) != 2:
        return "Использование: /delete_hunter <tg_id>"
    try:
        return int(parts[1])
    except ValueError:
        return "❌ tg_id должен быть числом"


async def _find_hunter(session: AsyncSession, tg_id: int):
    result = await session.execute(select(Hunter).where(Hunter.tg_id == tg_id))
    return result.scalar_one_or_none()


async def delete_hunter_by_tg_id_and_get_text(text: str) -> str:
    async with AsyncSessionLocal() as session:
        parsed = await _parse_tg_id(text)
        if isinstance(parsed, str):
            return parsed

        tg_id = parsed
        hunter = await _find_hunter(session, tg_id)
        if not hunter:
            return "Охотник не найден"

        await session.delete(hunter)
        await session.commit()
        return f"✅ Охотник с Telegram ID {tg_id} удалён"


# ========= Удаление заявки охотника =========
async def _parse_tg_id_from_command(text: str) -> int | str:
    parts = text.split()
    if len(parts) != 2:
        return "Использование: /delete_request <tg_id>"
    try:
        return int(parts[1])
    except ValueError:
        return "❌ tg_id должен быть числом"


async def find_hunter_request_by_tg_id(session: AsyncSession, tg_id: int) -> str:
    result = await session.execute(
        select(Hunter).where(Hunter.tg_id == tg_id).options(selectinload(Hunter.request))
    )
    hunter_obj = result.scalar_one_or_none()

    if not hunter_obj:
        return "Охотник не найден"
    if not hunter_obj.request:
        return "У охотника нет заявки"

    await session.delete(hunter_obj.request)
    await session.commit()
    return f"✅ Заявка охотника с Telegram ID {tg_id} удалена"


async def handle_delete_request_command(text: str) -> str:
    async with AsyncSessionLocal() as session:
        parsed_tg_id = await _parse_tg_id_from_command(text)
        if isinstance(parsed_tg_id, str):
            return parsed_tg_id

        return await find_hunter_request_by_tg_id(session, parsed_tg_id)


# ========= Вернуть все охотничьи базы =========
async def _fetch_all_hunting_bases(session: AsyncSession):
    stmt = select(HuntingBase).options(selectinload(HuntingBase.services))
    result = await session.scalars(stmt)
    return result.all()


def _format_hunting_base(base: HuntingBase, index: int) -> str:
    services_list = ', '.join(service.name for service in base.services) if base.services else '—'
    return (
        f"{index}. {base.name}\n"
        f"   Telegram ID: {base.tg_id}\n"
        f"   Region: {base.region}\n"
        f"   Contact person: {base.contact_person}\n"
        f"   Contact: {base.contact}\n"
        f"   Website: {base.website or '—'}\n"
        f"   Services: {services_list}\n"
    )


async def get_all_hunting_bases() -> str:
    async with AsyncSessionLocal() as session:
        bases = await _fetch_all_hunting_bases(session)
        if not bases:
            return "📋 Нет зарегистрированных охотничьих баз."

        lines = ["📋 Список всех охотничьих баз:\n"]
        for i, base in enumerate(bases, 1):
            lines.append(_format_hunting_base(base, i))
        return '\n'.join(lines).strip()


# ========= Удаление охотничьей базы по tg_id =========
async def _parse_hunting_base_tg_id(text: str) -> int | str:
    parts = text.split()
    if len(parts) != 2:
        return "Использование: /delete_hunting_base <tg_id>"
    try:
        return int(parts[1])
    except ValueError:
        return "❌ tg_id должен быть числом"


async def _find_hunting_base(session: AsyncSession, tg_id: int) -> HuntingBase | None:
    result = await session.execute(select(HuntingBase).where(HuntingBase.tg_id == tg_id))
    return result.scalar_one_or_none()


async def delete_hunting_base_by_tg_id_and_get_text(text: str) -> str:
    async with AsyncSessionLocal() as session:
        parsed = await _parse_hunting_base_tg_id(text)
        if isinstance(parsed, str):
            return parsed

        tg_id = parsed
        base = await _find_hunting_base(session, tg_id)
        if not base:
            return f"Охотничья база с Telegram ID {tg_id} не найдена"

        await session.delete(base)
        await session.commit()
        return f"✅ Охотничья база с Telegram ID {tg_id} удалена"
