from pathlib import Path

from exceptions import UserNotFoundError
from stores.base_store import BaseStore
from stores.user import User


class UsersStore(BaseStore):

    def __init__(self) -> None:

        super().__init__(Path(__file__).resolve().parent.parent / 'data/users.json', User)

    @property
    def users(self) -> list[User]:
        return self.records

    def add_user(self, user: User):
        self.add_record(user)

    def get_users_by_login(self, login: str):
        return list(filter(lambda u: u.login == login, self.users))

    def get_user_by_id(self, id_: str) -> User:
        for user in self.users:
            if user.id_ == id_:
                return user

        raise UserNotFoundError('User not found by id')

    def block_user(self):
        self.blocked = True
