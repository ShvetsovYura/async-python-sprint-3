from user import User


class UsersStore:

    def __init__(self) -> None:
        self._users: list[User] = []
        self._users.append(User(id_='asdflka', name='Pipa', chats=['public']))
        self._block_timeout = 60.0

    @property
    def users(self) -> list[User]:
        return self._users

    def get_user_by_id(self, id_: str) -> User:
        for user in self._users:
            if user.id_ == id_:
                return user

        raise Exception('User not found by id')

    def block_user(self, block_timeout=60.0):
        self.blocked = True