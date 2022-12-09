import asyncio
import dataclasses
import json
import logging
import uuid
from pathlib import Path

from encoders import EnhancedJsonEncoder
from exceptions import RoomNameExistsUsedError
from stores.room import Room
from stores.singleton import SingletonType

logger = logging.getLogger(__name__)

default_room = Room(id_='edb74300-247c-494a-9eed-308d69667ff3', name='public')


class RoomStore(metaclass=SingletonType):

    def __init__(self):
        self._rooms = []
        self._path = Path(__file__).resolve().parent.parent / 'data/rooms.json'

        if not self._path.exists():
            self._create_default_room()

        self._read_all_rooms()

    @property
    def rooms(self):
        return self._rooms

    def add_room(self, name: str, user: str):
        rooms_ = self.get_rooms_by_name(name)
        if rooms_:
            raise RoomNameExistsUsedError()

        self._rooms.append(Room(id_=str(uuid.uuid4()), name=name, owner=user))

    def get_rooms_by_name(self, name: str):
        return list(filter(lambda r: r.name == name, self._rooms))

    async def dump_rooms(self):
        while True:

            await asyncio.sleep(5 * 60)

            async with asyncio.Lock():
                with open(self._path, 'w') as file:
                    _rooms = [dataclasses.asdict(room) for room in self._rooms.copy()]
                    file.write(json.dumps(_rooms, cls=EnhancedJsonEncoder, indent=2))

                    logger.info('dump rooms successful')

    def _read_all_rooms(self):
        with open(self._path, 'r') as file:
            _rooms = file.read()
            if _rooms == '':
                self._rooms = [default_room]
                return

            self._rooms = [Room(**room) for room in json.loads(_rooms)]

    def _create_default_room(self):
        with open(self._path, 'w') as file:
            room_ = dataclasses.asdict(default_room)
            file.write(json.dumps([room_], cls=EnhancedJsonEncoder, indent=2))
