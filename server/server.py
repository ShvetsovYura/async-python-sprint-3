import asyncio
import logging
from asyncio.streams import StreamReader, StreamWriter

from server.connected_client import ChatRoom, ConnectedUser

logger = logging.getLogger(__name__)


class Server:

    def __init__(self, host='127.0.0.1', port=8000):
        self._host = host
        self._port = port
        self._clients: list[ConnectedUser] = []
        self._rooms: dict[str, ChatRoom] = {'shared': ChatRoom('shared')}

    def listen(self):
        logger.info(f'server start at {self._host}:{self._port}')
        asyncio.run(self._start_server())

    async def _start_server(self):
        server = await asyncio.start_server(self._accept_client_connection, self._host, self._port)

        async with server:
            await server.serve_forever()

    async def _accept_client_connection(self, reader: StreamReader, writer: StreamWriter):
        writer.write('Please, enter you name: '.encode())
        await writer.drain()
        try:
            # Ждем ввода имени пользователя
            raw_name = await asyncio.wait_for(asyncio.create_task(reader.read(1024)), timeout=20.0)
            name = raw_name.decode().strip()
            writer.write(f'Hello, {name}. Welcome to chat\r\n Please enter you message: '.encode())
            await writer.drain()

        except asyncio.TimeoutError:
            writer.write('Timeout '.encode())
            await writer.drain()
            writer.close()

        else:
            clients_by_name: list[ConnectedUser] = list(
                filter(lambda client: name == client.name, self._clients))

            if clients_by_name:
                # Клиент с таким именем уже есть
                client = clients_by_name[0]
                client.add_connection(reader=reader, writer=writer)
            else:
                # Клиента нет, создаем новый
                user = ConnectedUser(name=name, reader=reader, writer=writer)
                self._clients.append(user)
                shared_room = self._rooms.get('shared')
                if shared_room:
                    shared_room.add_user(user)
                await self._send_all_except(name, '\r\nUser: {} connected'.format(name))

    async def _send_all_except(self, username: str, message: str):
        other_users = filter(lambda u: u.name != username, self._clients)

        for user in other_users:
            await user.send_message(message)

    async def _broadcast_message(self, message):
        for client in self._clients:
            await client.send_message(message)


if __name__ == '__main__':
    srv = Server()
    srv.listen()
