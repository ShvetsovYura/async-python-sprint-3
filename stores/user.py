import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


def get_default_blocks() -> dict[str, Optional[datetime]]:
    return {'public': None}


@dataclass
class User:
    id_: str
    name: str
    password: str
    # rooms: list[str]

    login: str = 'user'
    blocked_in_chats: dict[str, Optional[datetime]] = field(default_factory=get_default_blocks)
    complaints: int = 0

    def set_complaint(self):
        self.complaints += 1

    def set_block_in_chat(self, chat_id, period: timedelta):
        self.blocked_in_chats[chat_id] = datetime.now() + period

    def set_unblock_in_chat(self, chat_id):
        self.blocked_in_chats[chat_id] = None

    def check_time_block_expired(self, chat_id):
        blocked_to = self.blocked_in_chats.get(chat_id)
        if blocked_to and blocked_to < datetime.now():
            self.set_unblock_in_chat(chat_id)

    def is_blocked_in_chat(self, chat_id):
        # если пользователя нет в списке банов

        self.check_time_block_expired(chat_id)

        chat_blocked_status = self.blocked_in_chats.get(chat_id)
        if not chat_blocked_status:
            return False
        else:
            return True if self.blocked_in_chats.get(chat_id) else False

    def check_login_password(self, login: str, password: str):
        if login == self.login and password == self.password:
            return True
        return False

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
