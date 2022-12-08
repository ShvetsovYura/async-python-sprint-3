import asyncio
import dataclasses
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from encoders import EnhancedJsonEncoder
from exceptions import OverflowSendMessagesUserBlocked
from message import ChatMessage
from stores.users_store import UsersStore

logger = logging.getLogger(__name__)


class MessagesStore:

    def __init__(self, users_store: UsersStore, dump_timeout=5.0) -> None:
        self._users_store = users_store
        self._dump_timeout = dump_timeout

        self._path = Path(__file__).resolve().parent.parent / 'data/messages.json'
        self._messages: list[ChatMessage] = []
        if not self._path.exists():
            with open(self._path, 'w+') as file:
                file.write('[]')

        self.read_all_messages()

    def read_all_messages(self):
        with open(self._path, 'r') as file:
            _messages = file.read()
            if _messages == '':
                return []

            self._messages = [ChatMessage(**msg) for msg in json.loads(_messages)]

    async def dump_message(self):
        while True:
            await asyncio.sleep(self._dump_timeout)

            async with asyncio.Lock():
                with open(self._path, 'w') as file:
                    _msgs = [dataclasses.asdict(msg) for msg in self._messages.copy()]
                    file.write(json.dumps(_msgs, cls=EnhancedJsonEncoder, indent=2))

                    logger.info("dump messages successful")

    def _get_send_user_messages_count_by_period(self, user_id: str):

        messages_in_interval = filter(
            lambda msg: msg.user_id == user_id and msg.created_at >= datetime.now() - timedelta(
                minutes=20), self._messages)
        return len(list(messages_in_interval))

    def add_message(self, message: ChatMessage):
        user = self._users_store.get_user_by_id(message.user_id)

        if user.is_blocked_in_chat(chat_id=message.chat_id):
            raise OverflowSendMessagesUserBlocked()

        self._messages.append(message)
        user.increase_message_in_chat(message.chat_id)

    def get_messages_for_user(self, user_id: str):
        user = self._users_store.get_user_by_id(user_id)

        _unread_messages = filter(
            lambda msg: msg.chat_id in user.chats and user_id not in msg.read_users,
            self._messages)

        return list(_unread_messages)
