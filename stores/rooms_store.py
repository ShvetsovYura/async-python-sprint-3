import logging
import uuid
from pathlib import Path

from exceptions import RoomNameExistsUsedError
from stores.base_store import BaseStore
from stores.room import Room

logger = logging.getLogger(__name__)

default_room = Room(id_='edb74300-247c-494a-9eed-308d69667ff3', name='public')


class RoomStore(BaseStore):

    def __init__(self):
        super().__init__(Path(__file__).resolve().parent.parent / 'data/rooms.json', Room)

        if not self.records:
            self.add_record(default_room)

    @property
    def rooms(self) -> list[Room]:
        return self.records

    def add_room(self, name: str, user: str):
        rooms_ = self.get_rooms_by_name(name)
        if rooms_:
            raise RoomNameExistsUsedError()

        self.records.append(Room(id_=str(uuid.uuid4()), name=name, owner=user))

    def get_rooms_by_name(self, name: str) -> list[Room]:
        return list(filter(lambda r: r.name == name, self.records))
