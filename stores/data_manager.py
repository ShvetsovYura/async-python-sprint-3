import asyncio
from datetime import datetime, timedelta
from typing import Optional

from exceptions import OverflowSendMessagesUserBlocked, UserLoginAlreadyExists
from stores.message import ChatMessage
from stores.messages_store import MessagesStore
from stores.rooms_store import RoomsStore
from stores.user import User
from stores.users_store import UsersStore


class DataManager:

    def __init__(self,
                 users_store: UsersStore,
                 rooms_store: RoomsStore,
                 messages_store: MessagesStore,
                 older_than_mins=20) -> None:

        self._users_store = users_store
        self._rooms_store = rooms_store
        self._messages_store = messages_store
        self._older_than_mins = older_than_mins

    @property
    def users_store(self):
        return self._users_store

    @property
    def rooms_store(self):
        return self._rooms_store

    @property
    def messages_store(self):
        return self._messages_store

    def get_users_in_room(self, room_id: str):
        room = self.get_room_by_id(room_id)
        if room:
            return room.users

    def create_user(self, login: str, name: str, pwd: str) -> User:
        """ Создание нового пользователя, по-умолчанию доабвляется в `public` """
        user_ = self.users_store.get_user_by_login(login)
        if user_:
            raise UserLoginAlreadyExists()

        new_user = self.users_store.crate_new_user(name, login, pwd)

        rooms = self.rooms_store.get_rooms_by_name('public')
        for room_ in rooms:
            room_.users.append(new_user.id_)
        return new_user

    def get_room_by_id(self, room_id):
        return self._rooms_store.get_room_by_id(room_id)

    def add_message(self, message: ChatMessage):
        user = self.users_store.get_user_by_id(message.user_id)

        if user.is_blocked_in_chat(chat_id=message.chat_id):
            raise OverflowSendMessagesUserBlocked()

        if self.get_user_messages_by_period_in_chat(user.id_, message.chat_id) > 5:
            user.set_block_in_chat(message.chat_id, timedelta(minutes=5))
            raise OverflowSendMessagesUserBlocked()

        self.messages_store.messages.append(message)

    def get_user_rooms(self, user_id):
        return list(filter(lambda room: user_id in room.users, self._rooms_store.rooms))

    def get_unread_user_messages(self, user_id: str):
        # непрочитанные сообщения для пользователя
        # выборка всех сообщений, где пользователь не является отправителем
        # и не содержится в списке прочитавших
        # а также пользвоатель состоит в списке этого чата
        user_rooms = self.get_user_rooms(user_id)

        def unread_messages_predicate(message: ChatMessage):
            if (message.chat_id in user_rooms) and (user_id not in message.read_users) and (
                    user_id != message.user_id):
                return True
            return False

        _unread_messages = filter(unread_messages_predicate, self.messages_store.get_messages())

        return list(_unread_messages)

    def get_user_messages_by_period_in_chat(self,
                                            user_id: str,
                                            room_id: str,
                                            back_period_sec: int = 300) -> int:
        """ Количество сообщений за период от пользователя в определенном чате """

        def user_messages_in_room_predicate(message: ChatMessage):
            if (message.chat_id == room_id) and (message.user_id == user_id) and (
                    message.created_at > datetime.now() - timedelta(seconds=back_period_sec)):
                return True
            return False

        return len(list(filter(user_messages_in_room_predicate, self.messages_store.messages)))

    def set_read_messages_by_user(self, messages_ids: list[str], user_id: str):
        for msg in self.messages_store.messages:
            for message_id in messages_ids:

                if msg.id_ == message_id:
                    msg.read_users.extend([user_id])

    async def run_remove_messages_older_than(self):
        while True:
            await asyncio.sleep(60)
            self.remove_messages_older_than()

    def remove_messages_older_than(self, interval: Optional[timedelta] = None):

        remove_after = interval if interval else timedelta(minutes=self._older_than_mins)

        data = list(
            filter(lambda msg: msg.created_at > datetime.now() - remove_after,
                   self.messages_store.messages))

        self.messages_store._set_messages(data)

    def remove_user_from_chat(self, user_id: str, room_id: str):
        room = self.get_room_by_id(room_id)
        if room:
            room.users.remove(user_id)
