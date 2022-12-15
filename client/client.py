import asyncio
import logging
import uuid
from asyncio.streams import StreamReader, StreamWriter
from typing import Optional

logger = logging.getLogger(__name__)


class Client:

    def __init__(self, server_host='127.0.0.1', server_port=8000):
        self._host = server_host
        self._port = server_port
        self._reader: Optional[StreamReader] = None
        self._writer: Optional[StreamWriter] = None
        asyncio.gather(asyncio.create_task(self.run_reader()))

    async def connect(self):
        self._reader, self._writer = await asyncio.open_connection(self._host, self._port)
        await self.send(uuid.uuid4().__str__())

    async def run_reader(self):
        while True:
            if self._reader:
                data = await self._reader.read(1024)
                logger.info(data.decode())

    async def send(self, message=''):
        if self._writer:
            self._writer.write(message.encode())
            await self._writer.drain()
