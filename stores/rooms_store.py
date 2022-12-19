import logging
import uuid
from pathlib import Path

from exceptions import RoomNameAlreadyExistsError
from stores.base_store import BaseStore
from stores.room import Room

logger = logging.getLogger(__name__)


class RoomsStore(BaseStore):

    path_to_file = Path(__file__).resolve().parent.parent / 'data/rooms.json'
    default_room = Room(id_='edb74300-247c-494a-9eed-308d69667ff3', name='public')

    def __init__(self, init_file: bool = True):
        super().__init__(self.path_to_file, Room, init_file_storage=init_file)

        if not self.records:
            self.add_record(self.default_room)

    @property
    def rooms(self) -> list[Room]:
        return self.records

    def add_room(self, name: str, owner_id: str):
        rooms_ = self.get_rooms_by_name(name)
        if rooms_:
            raise RoomNameAlreadyExistsError()

        self.records.append(Room(id_=str(uuid.uuid4()), name=name, owner=owner_id))

    def get_rooms_by_name(self, name: str) -> list[Room]:
        return list(filter(lambda r: r.name == name, self.records))

    def get_room_by_id(self, id_: str):
        rooms_ = list(filter(lambda r: r.id_ == id_, self.rooms))
        if rooms_:
            return rooms_[0]

        return None
