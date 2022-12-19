import uuid
from datetime import datetime, timedelta
from unittest import TestCase

from exceptions import OverflowSendMessagesUserBlocked, UserLoginAlreadyExists
from stores.data_manager import DataManager
from stores.message import ChatMessage
from stores.messages_store import MessagesStore
from stores.rooms_store import RoomsStore
from stores.users_store import UsersStore


class TestDataManager(TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.mgr_ = DataManager(users_store=UsersStore(init_file=False),
                                rooms_store=RoomsStore(init_file=False),
                                messages_store=MessagesStore(init_file=False))

        self.mgr_.messages_store._clear()

    def test_create_user(self):
        new_user = self.mgr_.create_user('test', 'pipa', ' 123456')

        self.assertIn(new_user, self.mgr_.users_store.users)

        with self.assertRaises(UserLoginAlreadyExists):
            self.mgr_.create_user('test', 'pipa', ' 123456')

        self.assertEqual(len(self.mgr_.users_store.users), 1)

    def test_add_message(self):
        new_user = self.mgr_.create_user('test', 'pipa', ' 123456')

        for _ in range(5):
            self.mgr_.add_message(
                ChatMessage('hohoho ' + str(uuid.uuid4()),
                            new_user.id_,
                            self.mgr_.rooms_store.default_room.id_,
                            read_users=[]))

        self.assertEqual(5, len(self.mgr_.messages_store.messages))

    def test_get_users_in_room(self):
        room_ = self.mgr_.get_room_by_id('edb74300-247c-494a-9eed-308d69667ff3')

        room_.users.clear()    # type: ignore
        for _ in range(123):
            self.mgr_.create_user(f'test_{str(uuid.uuid4())}', 'pipa', ' 123456')

        self.assertIsNotNone(room_)
        self.assertEqual(123, len(room_.users))    # type: ignore

    def test_add_message_overload(self):
        new_user = self.mgr_.create_user('test', 'pipa', ' 123456')

        with self.assertRaises(OverflowSendMessagesUserBlocked):
            for _ in range(150):
                self.mgr_.add_message(
                    ChatMessage('hohoho ' + str(uuid.uuid4()),
                                new_user.id_,
                                self.mgr_.rooms_store.default_room.id_,
                                read_users=[]))

    def test_get_user_rooms(self):
        new_user = self.mgr_.create_user('test', 'pipa', ' 123456')

        rooms = self.mgr_.get_user_rooms(new_user.id_)

        self.assertIn(self.mgr_.rooms_store.default_room, rooms)

    def test_remove_user_from_chat(self):

        room_ = self.mgr_.get_room_by_id('edb74300-247c-494a-9eed-308d69667ff3')
        room_.users.clear()    # type: ignore
        new_user = self.mgr_.create_user('test', 'pipa', ' 123456')

        self.assertEqual(1, len(room_.users))    # type: ignore

        self.mgr_.remove_user_from_chat(new_user.id_, self.mgr_.rooms_store.default_room.id_)

        self.assertEqual(0, len(room_.users))    # type: ignore

    def test_remove_messages_older_than(self):
        new_user = self.mgr_.create_user('test', 'pipa', ' 123456')
        room_ = self.mgr_.get_room_by_id('edb74300-247c-494a-9eed-308d69667ff3')
        for _ in range(3):
            self.mgr_.add_message(
                ChatMessage(
                    str(uuid.uuid4),
                    user_id=new_user.id_,
                    chat_id=room_.id_,    # type: ignore
                    created_at=datetime.now() - timedelta(minutes=30)))

        self.mgr_.add_message(
            ChatMessage(
                str(uuid.uuid4),
                user_id=new_user.id_,
                chat_id=room_.id_,    # type: ignore
                created_at=datetime.now()))

        self.mgr_.remove_messages_older_than(timedelta(minutes=20))

        self.assertEqual(1, len(self.mgr_.messages_store.messages))

    def test_set_messages_user_read_status(self):
        new_user = self.mgr_.create_user('test', 'pipa', ' 123456')
        room_ = self.mgr_.get_room_by_id('edb74300-247c-494a-9eed-308d69667ff3')
        for _ in range(3):
            self.mgr_.add_message(
                ChatMessage(
                    str(uuid.uuid4),
                    user_id=new_user.id_,
                    chat_id=room_.id_,    # type: ignore
                    created_at=datetime.now() - timedelta(minutes=30)))

        msg_lst = [self.mgr_.messages_store.messages[0].id_]
        self.mgr_.set_read_messages_by_user(msg_lst, user_id=new_user.id_)

        self.assertEqual(1, len(self.mgr_.messages_store.messages[0].read_users))
