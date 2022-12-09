import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


def get_default_chat():
    return {'public': 0}


def get_default_blocks() -> dict[str, Optional[datetime]]:
    return {'public': None}


@dataclass
class User:
    id_: str
    name: str
    password: str
    rooms: list[str]

    login: str = 'user'
    blocked_in_chats: dict[str, Optional[datetime]] = field(default_factory=get_default_blocks)
    complaints: int = 0
    messages_in_chats: dict[str, int] = field(default_factory=get_default_chat)

    def is_blocked_in_chat(self, chat_id):
        return self.blocked_in_chats[chat_id]

    def check_login_password(self, login: str, password: str):
        if login == self.login and password == self.password:
            return True
        return False

    def increase_message_in_chat(self, chat_id: str):

        self.messages_in_chats[chat_id] = self.messages_in_chats.get(chat_id, 0) + 1

        count = self.messages_in_chats.get(chat_id, 0)
        if count > 5:
            self.blocked_in_chats[chat_id] = datetime.now()

    async def reset_message_count(self):
        """ Интервально обнуляет количество отправленных сообщений """

        while True:
            await asyncio.sleep(5 * 60)
            for key, _ in self.messages_in_chats.items():
                self.messages_in_chats[key] = 0
                self.blocked_in_chats[key] = None

    async def check_blocked(self, timeout=20.0):
        """ Проверка времени для разблокироваки пользователя """

        while True:
            await asyncio.sleep(1)

            async with asyncio.Lock():

                if not self.blocked:
                    continue
                if self.blocked + timedelta(seconds=timeout) < datetime.now():
                    logger.info(f'unblock user: {self.name}')
                    self.blocked = None
                    self.messages_in_period = 0
