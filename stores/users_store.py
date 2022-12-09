from exceptions import UserNotFoundError
from stores.singleton import SingletonType
from stores.user import User


class UsersStore(metaclass=SingletonType):

    def __init__(self) -> None:
        self._users: list[User] = []

        self._block_timeout = 60.0

    @property
    def users(self) -> list[User]:
        return self._users

    def get_users_by_login(self, login: str):
        return list(filter(lambda u: u.login == login, self._users))

    def get_user_by_id(self, id_: str) -> User:
        for user in self._users:
            if user.id_ == id_:
                return user

        raise UserNotFoundError('User not found by id')

    def block_user(self, block_timeout=60.0):
        self.blocked = True
