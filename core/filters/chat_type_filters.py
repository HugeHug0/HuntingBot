from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

private = "private"
group = "group"
supergroup = "supergroup"
chanel = "channel"
sender = "sender"


class PrivateChatFilter(BaseFilter):
    def __init__(self, tg_chat_types: list):
        self.tg_chat_types = tg_chat_types

    async def __call__(self, event) -> bool:

        if isinstance(event, Message):
            chat_type = event.chat.type
        elif isinstance(event, CallbackQuery) and event.message:
            chat_type = event.message.chat.type
        else:
            return False

        return chat_type in self.tg_chat_types

