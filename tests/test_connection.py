import asyncio
from unittest import IsolatedAsyncioTestCase

from client import Client
from server import Server


class TestConnection(IsolatedAsyncioTestCase):

    async def test_con(self):
        srv = Server()

        self.run(srv.listen())

        client = Client(server_host='0.0.0.0')
        await client.connect()

        self.assertEqual(1, 1)
