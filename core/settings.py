from environs import Env
from dataclasses import dataclass

@dataclass()
class Bots:  # Класс для хранения данных для бота
    bot_token: str
    db_dsn: str


@dataclass()
class Settings:
    bots: Bots
    request_group_id: int
    admin_ids: list
    chat_members_link: str


def get_settings(path: str = None):
    env = Env()
    env.read_env(path)  # Чтение переменных окружения

    db_user = env.str("POSTGRES_USER")
    db_password = env.str("POSTGRES_PASSWORD")
    db_name = env.str("POSTGRES_DB")
    db_host = env.str("DB_HOST", "db")
    db_port = env.str("DB_PORT", "5432")

    request_group_id = env.int('REQUESTS_GROUP_ID')
    chat_members_link = env.str('CHAT_MEMBERS_LINK')
    admin_ids = [int(i) for i in env.str('ADMIN_IDS').split(',')]

    db_dsn = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    return Settings(  # Создание dataclass для хранения данных
        bots=Bots(
            bot_token=env.str('BOT_TOKEN'),
            db_dsn=db_dsn
        ),
        request_group_id=request_group_id,
        admin_ids=admin_ids,
        chat_members_link=chat_members_link,
    )

settings = get_settings()
