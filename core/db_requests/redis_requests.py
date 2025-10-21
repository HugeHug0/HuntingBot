from core.db.redis import redis_client


async def get_value_from_cache_by_tg_id(tg_id: int | str):
    """Возвращает значение из Redis по Telegram ID"""
    key = f"user:{tg_id}"
    value = await redis_client.get(key)
    return value
