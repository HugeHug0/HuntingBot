from core.settings import settings

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

POSTGRES_DSN = settings.postgres_dsn
if not POSTGRES_DSN:
    raise RuntimeError("POSTGRES_DSN not set in environment")

engine = create_async_engine(POSTGRES_DSN, echo=True, future=True)

# асинхронный session maker
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession, future=True)

Base = declarative_base()
