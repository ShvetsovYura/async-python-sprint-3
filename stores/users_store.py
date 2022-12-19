import uuid
from pathlib import Path
from typing import Union

from exceptions import UserNotFoundError
from stores.base_store import BaseStore
from stores.user import User


class UsersStore(BaseStore):
    path_to_file = Path(__file__).resolve().parent.parent / 'data/users.json'

    def __init__(self, init_file: bool = True) -> None:

        super().__init__(self.path_to_file, User, init_file_storage=init_file)

    @property
    def users(self) -> list[User]:
        return self.records

    def crate_new_user(self, name: str, login: str, password: str) -> User:
        """ Сощдает нового пользователя и добавляет в список пользоватеей """

        new_user = User(id_=str(uuid.uuid4()), name=name, login=login, password=password)
        self.add_user(new_user)
        return new_user

    def add_user(self, user: User):
        self.add_record(user)

    def get_users_by_name(self, name: str) -> list[User]:
        return list(filter(lambda user: user.name == name, self.users))

    def get_user_by_login(self, login: str) -> Union[User, None]:
        users_ = list(filter(lambda u: u.login == login, self.users))
        if users_:
            return users_[0]
        return None

    def get_user_by_id(self, id_: str) -> User:
        for user in self.users:
            if user.id_ == id_:
                return user

        raise UserNotFoundError('User not found by id')

    def block_user(self):
        self.blocked = True
