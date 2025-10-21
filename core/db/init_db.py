from core.db.postgres import engine, Base


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def on_startup():
    await init_db()
