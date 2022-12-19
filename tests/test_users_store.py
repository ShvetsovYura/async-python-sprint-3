import uuid
from unittest import TestCase

from exceptions import UserNotFoundError
from stores.user import User
from stores.users_store import UsersStore


class TestUsersStore(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.us = UsersStore(False)

    def test_users_store_init(self):
        result = self.us.users

        self.assertEqual(0, len(result))

    def test_add_user(self):
        user = User(id_=str(uuid.uuid4()), name='Pipa', login='pipa', password='pwd')
        self.us.add_user(user)

        self.assertEqual(1, len(self.us.users))

    def test_create_new_user(self):
        user = self.us.crate_new_user('Pipa', 'pipa', 'pwd')

        usr_in_store = self.us.users[0]

        self.assertEqual(1, len(self.us.users))
        self.assertEqual(user.id_, usr_in_store.id_)

    def test_get_user_by_login(self):
        user = self.us.crate_new_user('Pipa', 'pipa', 'pwd')

        result = self.us.get_user_by_login(user.login)

        self.assertIsNotNone(result)
        self.assertEqual(user.id_, result.id_)    # type: ignore

    def test_get_user_by_id(self):
        user = self.us.crate_new_user('Pipa', 'pipa', 'pwd')

        found_user = self.us.get_user_by_id(user.id_)

        self.assertEqual(user.id_, found_user.id_)

    def test_get_user_by_id_notfound(self):

        with self.assertRaises(UserNotFoundError):
            self.us.get_user_by_id(str(uuid.uuid4()))
