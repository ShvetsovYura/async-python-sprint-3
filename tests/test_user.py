import uuid
from datetime import datetime, timedelta
from unittest import TestCase

from stores.user import User


class TestUsers(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.user = User(login='test_user',
                         password='test_password',
                         id_=str(uuid.uuid4()),
                         name='TestUserName')

    def test_check_user_and_password(self):

        result = self.user.check_login_password(login='test_user', password='test_password')

        self.assertTrue(result)

    def test_check_user_and_password_bad_login(self):

        result = self.user.check_login_password(login='login', password='test_password')
        self.assertFalse(result)

    def test_check_user_and_password_bad_password(self):
        result = self.user.check_login_password(login='test_user', password='abracadabra')

        self.assertFalse(result)

    def test_is_blocked_in_chat_blocked(self):
        chat_id_ = 'chat_1235_'
        self.user.set_block_in_chat(chat_id_, timedelta(minutes=1))
        result = self.user.is_blocked_in_chat(chat_id_)

        self.assertTrue(result)

    def test_is_blocked_in_chat_notblock(self):
        chat_id_ = 'caht_123'
        self.user.blocked_in_chats[chat_id_] = datetime.now()
        result = self.user.is_blocked_in_chat(chat_id=chat_id_)

        self.assertFalse(result)

    def test_time_block_expires_not_expired(self):

        chat_id_ = 'caht_123'
        blocked_to = datetime.now() + timedelta(minutes=20)
        self.user.blocked_in_chats[chat_id_] = blocked_to

        self.user.check_time_block_expired(chat_id_)

        result = self.user.blocked_in_chats.get(chat_id_)

        self.assertIsNotNone(result)

    def test_time_block_expires_is_expired(self):

        chat_id_ = 'caht_123'
        blocked_to = datetime.now()
        self.user.blocked_in_chats[chat_id_] = blocked_to

        self.user.check_time_block_expired(chat_id_)

        result = self.user.blocked_in_chats.get(chat_id_)

        self.assertIsNone(result)
