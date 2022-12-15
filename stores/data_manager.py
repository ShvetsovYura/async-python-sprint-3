import asyncio
import uuid
from datetime import datetime, timedelta

from exceptions import OverflowSendMessagesUserBlocked, UserLoginAlreadyExists
from stores.message import ChatMessage
from stores.messages_store import MessagesStore
from stores.rooms_store import RoomStore
from stores.singleton import SingletonType
from stores.user import User
from stores.users_store import UsersStore


class DataManager(metaclass=SingletonType):

    def __init__(self, older_than_mins=20) -> None:
        self._users_store = UsersStore()
        self._room_store = RoomStore()
        self._messages_store = MessagesStore()
        self._older_than_mins = older_than_mins

    @property
    def users_store(self):
        return self._users_store

    @property
    def rooms_store(self):
        return self._room_store

    @property
    def messages_store(self):
        return self._messages_store

    def get_users_in_room(self, room_id: str):
        room = self.get_room_by_id(room_id)
        if room:
            return room.users

    def add_user(self, login: str, name: str, pwd: str):
        """ Создание нового пользователя, по-умолчанию доабвляется в `public` """
        users_ = self.users_store.get_users_by_login(login)
        if users_:
            raise UserLoginAlreadyExists()

        new_user = User(id_=str(uuid.uuid4()), name=name, login=login, password=pwd)
        self.users_store.add_user(new_user)

        rooms = self.rooms_store.get_rooms_by_name('public')
        for room_ in rooms:
            room_.users.append(new_user.id_)

    def get_room_by_id(self, room_id):
        return self._room_store.get_room_by_id(room_id)

    def add_message(self, message: ChatMessage):
        user = self.users_store.get_user_by_id(message.user_id)

        if user.is_blocked_in_chat(chat_id=message.chat_id):
            raise OverflowSendMessagesUserBlocked()

        if self.get_user_messages_by_period_in_chat(user.id_, message.chat_id) > 5:
            user.set_block_in_chat(message.chat_id, timedelta(minutes=5))
            raise OverflowSendMessagesUserBlocked()

        self.messages_store.messages.append(message)

    def get_user_rooms(self, user_id):
        return list(filter(lambda room: user_id in room.users, self._room_store.rooms))

    def get_unread_user_messages(self, user_id: str):
        # непрочитанные сообщения для пользователя
        # выборка всех сообщений, где пользователь не является отправителем
        # и не содержится в списке прочитавших
        # а также пользвоатель состоит в списке этого чата
        user_rooms = self.get_user_rooms(user_id)

        _unread_messages = filter(
            lambda msg: msg.chat_id in user_rooms and user_id not in msg.read_users and user_id !=
            msg.user_id, self.messages_store.get_messages())

        return list(_unread_messages)

    def get_user_messages_by_period_in_chat(self,
                                            user_id: str,
                                            room_id: str,
                                            back_period_sec: int = 300) -> int:
        """ Количество сообщений за период от пользователя в определенном чате """

        return len(
            list(
                filter(
                    lambda m: m.chat_id == room_id and m.user_id == user_id and m.created_at >
                    datetime.now() - timedelta(seconds=back_period_sec),
                    self.messages_store.messages)))

    def set_messages_user_read_status(self, messages_ids: list[str], user_id: str):
        for msg in self.messages_store.messages:
            for message_id in messages_ids:

                if msg.id_ == message_id:
                    msg.read_users.extend([user_id])

    async def run_remove_messages_older_than(self):
        while True:
            await asyncio.sleep(60)
            self.remove_messages_older_than()

    def remove_messages_older_than(self):
        data = list(
            filter(
                lambda msg: msg.created_at < datetime.now() - timedelta(
                    minutes=self._older_than_mins), self.messages_store.messages))

        self.messages_store._set_messages(data)

    def remove_user_from_chat(self, user_id: str, room_id: str):
        room = self.get_room_by_id(room_id)
        if room:
            room.users.remove(user_id)
