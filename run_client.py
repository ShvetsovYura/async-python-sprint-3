import asyncio
from client.client import Client

if __name__ == '__main__':
    client = Client(server_port=8001)
    asyncio.run(client.connect())
