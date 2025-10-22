from sqlalchemy import delete
from core.db.postgres import AsyncSessionLocal
from core.db.models import Hunter, HuntingBase
from core.db_requests.redis_requests import delete_value_from_cache_by_tg_id


async def _delete_from_postgres(tg_id: int):
    async with AsyncSessionLocal() as session:
        await session.execute(delete(Hunter).where(Hunter.tg_id == tg_id))
        await session.execute(delete(HuntingBase).where(HuntingBase.tg_id == tg_id))
        await session.commit()


async def _delete_from_redis(tg_id: int):
    await delete_value_from_cache_by_tg_id(tg_id)


async def delete_user_by_tg_id(tg_id: int):
    """Удаляет пользователя из всех источников данных."""
    await _delete_from_postgres(tg_id)
    await _delete_from_redis(tg_id)
