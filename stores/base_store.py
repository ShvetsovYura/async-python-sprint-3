import asyncio
import dataclasses
import json
import logging
from typing import Callable

from utils import EnhancedJsonEncoder, json_object_hook

logger = logging.getLogger(__name__)


class BaseStore:

    def __init__(self, path, class_type: Callable, dump_timeout: int = 60):
        self._path = path

        self._dump_timeout = dump_timeout
        self._class_type = class_type

        if not self._path.exists():
            with open(self._path, 'w+') as file:
                file.write(json.dumps([]))

        self._records = self.read_records_from_storage(path, class_type)

    @property
    def records(self) -> list:
        return self._records

    @staticmethod
    def read_records_from_storage(path, class_type):
        with open(path, 'r') as file:
            _records = file.read()

            if not _records:
                return []

            return [
                class_type(**record)
                for record in json.loads(_records, object_hook=json_object_hook)
            ]

    def add_record(self, record):
        self._records.append(record)

    async def dump_records(self):
        while True:
            await asyncio.sleep(self._dump_timeout)

            async with asyncio.Lock():
                with open(self._path, 'w') as file:
                    _records = [dataclasses.asdict(record) for record in self._records]
                    file.write(json.dumps(_records, cls=EnhancedJsonEncoder, indent=2))

                    logger.info(f'dumps records for {str(self._class_type)}')
