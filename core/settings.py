from environs import Env
from dataclasses import dataclass

@dataclass()
class Bots:  # Класс для хранения данных для бота
    bot_token: str
    request_group_id: int
    admin_ids: list
    chat_members_link: str


@dataclass()
class Settings:
    bots: Bots
    postgres_dsn: str
    redis_host: str
    redis_port: int
    redis_db: int


def get_settings(path: str = None):
    env = Env()
    env.read_env(path)  # Чтение переменных окружения

    db_user = env.str("POSTGRES_USER")
    db_password = env.str("POSTGRES_PASSWORD")
    db_name = env.str("POSTGRES_DB")
    db_host = env.str("DB_HOST", "db")
    db_port = env.str("DB_PORT", "5432")

    redis_host = env.str("REDIS_HOST", "redis")
    redis_port = env.int("REDIS_PORT", 6379)
    redis_db = env.int("REDIS_DB", 0)

    postgres_dsn = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    request_group_id = env.int('REQUESTS_GROUP_ID')
    chat_members_link = env.str('CHAT_MEMBERS_LINK')
    admin_ids = [int(i) for i in env.str('ADMIN_IDS').split(',')]

    return Settings(  # Создание dataclass для хранения данных
        bots=Bots(
            bot_token=env.str('BOT_TOKEN'),
            request_group_id=request_group_id,
            admin_ids=admin_ids,
            chat_members_link=chat_members_link
        ),
        postgres_dsn=postgres_dsn,
        redis_host=redis_host,
        redis_port=redis_port,
        redis_db=redis_db
    )

settings = get_settings()
