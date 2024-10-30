from typing import Union

from aiogram import Router
from aiogram import Bot
from aiogram.types import Message

import config
from aiogram.filters import BaseFilter

router = Router()


class IsChatAdmin(BaseFilter):
    async def __call__(self, mq: Union[Message], bot: Bot) -> bool:
        chat = mq.chat if isinstance(mq, Message) else mq.message.chat
        chat_admins = await bot.get_chat_administrators(chat.id)
        chat_admin_ids = frozenset((member.user.id for member in chat_admins))

        return mq.from_user.id in chat_admin_ids


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type
