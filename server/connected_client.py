import asyncio
import logging
import uuid
from asyncio.streams import StreamReader, StreamWriter
from collections import UserList
from datetime import timedelta
from typing import Callable, Iterable, Optional

logger = logging.getLogger(__name__)


class ChatRoom:

    def __init__(self, name: str) -> None:
        self._name = name
        self._owner = None

        self._users: list[ConnectedUser] = []

    def add_user(self, user: 'ConnectedUser'):
        self._users.append(user)

    async def send_all(self, message):
        for user in self._users:
            await user.send_message(message)


class ChatConnection:

    def __init__(self, reader, writer, on_disconnect: Callable) -> None:
        self._writer: StreamWriter = writer
        self._reader: StreamReader = reader
        self._id = uuid.uuid4()
        self._on_disconnect_callback = on_disconnect

    @property
    def id_(self):
        return str(self._id)

    async def send_message(self, message: str):
        self._writer.write(message.encode())
        await self._writer.drain()

    async def wait_imcoming_message(self):
        logger.info('task waiter run....')
        while True:
            raw_msg = await self._reader.read(1024)
            if not raw_msg:
                break

            logger.info(f'receive msg: {raw_msg.decode()}')

        logger.info('end')
        self._writer.close()
        self._on_disconnect_callback(self.id_)


class ConnectionsList(UserList):

    def __init__(self, items: Iterable[ChatConnection]):
        for item in items:
            asyncio.create_task(item.wait_imcoming_message())
        super().__init__()

    def append(self, item: ChatConnection) -> None:
        asyncio.create_task(item.wait_imcoming_message())
        self.data.append(item)

    def remove(self, id_: str):
        logger.info('start remove by id', id_)

        data = self.data.copy()
        for connection in filter(lambda c: c.id == id_, data):
            self.data.remove(connection)

        logger.info('after filtered ')


class ConnectedUser:

    def __init__(
            self,
            reader: StreamReader,    # чтение сообщений от сервера
            writer: StreamWriter,    # запись сообщений в сокет
            name: str,    # имя пользователя
            limit_messages_at_period: int = 20,
            period: timedelta = timedelta(minutes=60.0),
    ) -> None:
        # делаем временные подключения, чтобы запросить имя пользователя
        self._temp_writer = writer
        self._temp_reader = reader
        self._name: Optional[str] = name
        self._connections = ConnectionsList([
            ChatConnection(reader=reader, writer=writer, on_disconnect=self.disconnect_connection),
        ])
        self._send_messages: int = 0

    @property
    def connections(self):
        """ Клиентские соединения """
        return self._connections

    @property
    def name(self):
        return self._name

    def disconnect_connection(self, id_: str):
        logger.info('start disconnect')
        self._connections.remove(id_)
        logger.info('call disconnect', len(self._connections))

    def increment_send_messages(self) -> None:
        self._send_messages += 1

    async def send_message(self, message: str):
        """ Отправлка сообщений всем инстансам подключений пользователя """
        self.increment_send_messages()
        logger.info(f'user: {self.name} sended: {self._send_messages}')
        for con in self._connections:
            await con.send_message(message)

    def add_connection(self, reader: StreamReader, writer: StreamWriter):
        self._connections.append(
            ChatConnection(reader=reader, writer=writer, on_disconnect=self.disconnect_connection))
