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

    def get_unread_user_messages(self, user_id: str):
        # пользователь по идентификатору
        user = self._users_store.get_user_by_id(user_id)

        # непрочитанные сообщения для пользователя
        # выборка всех сообщений, где пользователь не является отправителем
        # и не содержится в списке прочитавших
        # а также пользвоатель состоит в списке этого чата

        _unread_messages = filter(
            lambda msg: msg.chat_id in user.rooms and user_id not in msg.read_users and user_id !=
            msg.user_id, self.messages_store.get_messages())

        return list(_unread_messages)

    def set_messages_user_read_status(self, messages_ids: list[str], user_id: str):
        for msg in self.messages_store.messages:
            for message_id in messages_ids:

                if msg.id_ == message_id:
                    msg.read_users.extend([user_id])