import uuid

from exceptions import OverflowSendMessagesUserBlocked, UserLoginAlreadyExists
from stores.message import ChatMessage
from stores.messages_store import MessagesStore
from stores.rooms_store import RoomStore
from stores.singleton import SingletonType
from stores.user import User
from stores.users_store import UsersStore


class DataManager(metaclass=SingletonType):

    def __init__(self) -> None:
        self._users_store = UsersStore()
        self._room_store = RoomStore()
        self._messages_store = MessagesStore()

    @property
    def users_store(self):
        return self._users_store

    @property
    def rooms_store(self):
        return self._room_store

    @property
    def messages_store(self):
        return self._messages_store

    def get_users_by_room(self, room_id: str):
        return list(filter(lambda u: room_id in u.rooms, self._users_store.users))

    def add_user(self, login: str, name: str, pwd: str):
        users_ = self.users_store.get_users_by_login(login)
        if users_:
            raise UserLoginAlreadyExists()

        rooms = self.rooms_store.get_rooms_by_name('public')
        self.users_store.add_user(
            User(id_=str(uuid.uuid4()), name=name, login=login, password=pwd,
                 rooms=[rooms[0].id_]))

    def add_message(self, message: ChatMessage):
        user = self.users_store.get_user_by_id(message.user_id)

        if user.is_blocked_in_chat(chat_id=message.chat_id):
            raise OverflowSendMessagesUserBlocked()

        self.messages_store.messages.append(message)
        user.increase_message_in_chat(message.chat_id)

    def get_messages_for_user(self, user_id: str):
        user = self._users_store.get_user_by_id(user_id)

        _unread_messages = filter(
            lambda msg: msg.chat_id in user.rooms and user_id not in msg.read_users,
            self.messages_store.messages)

        return list(_unread_messages)
