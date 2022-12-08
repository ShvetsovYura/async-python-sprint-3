import asyncio
import logging
import logging.config
from asyncio.streams import StreamReader, StreamWriter
from datetime import datetime
from typing import Callable, Optional, TypedDict

import yaml

from exceptions import ResponseError, ValidateEntityError
from http_consts import HTTPMethod
from http_request import HttpRequest
from http_response import HttpResponse
from message import ChatMessage
from stores.messages_store import MessagesStore
from stores.users_store import UsersStore

logger = logging.getLogger(__name__)

users_store = UsersStore()
messages_store = MessagesStore(users_store=users_store)


class RouteData(TypedDict):
    method: HTTPMethod
    handler: Callable
    middlewares: list[Callable]
    kwargs: dict


class WebServer:
    """ Кастомная реализация web-сервера в упрощенном виде """

    def __init__(self, host='127.0.0.1', port=8000):
        self._host = host
        self._port = port
        self._router: dict[str, RouteData] = {}

    async def listen(self):
        logger.info(f'server start at {self._host}:{self._port}')
        asyncio.create_task(messages_store.dump_message())
        asyncio.gather(*[user.reset_message_count() for user in users_store.users])

        await asyncio.create_task(self._start_server())

    def route(self,
              url: str,
              method: HTTPMethod,
              middlewares: Optional[list[Callable]] = None,
              **kwargs):
        """ Декоратор для связывания роута и обработчика """

        def _route(_handler: Callable):
            self._router[url] = {
                'method': method,
                'handler': _handler,
                'middlewares': middlewares or [],
                'kwargs': kwargs,
            }
            return _handler

        return _route

    async def _start_server(self) -> None:
        server = await asyncio.start_server(self._accept_request, self._host, self._port)

        async with server:
            await server.serve_forever()

    async def _read_stream(self, reader: StreamReader) -> bytes:
        """ Читает входящий `сырой` http запрос """
        request_data = b''
        while True:
            request_data += await reader.read(1024)
            reader.feed_eof()
            if reader.at_eof():
                break
        return request_data

    async def _handle_router(self, request: HttpRequest) -> HttpResponse:
        """ На основе запроса вызывает обработчик о обрабатывает результат"""

        route = self._router.get(request.path)
        response = HttpResponse()
        response.headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-powered-by': 'simple-json-server',
        }

        if not route:
            # если не найдено роута
            response.status_code = 404
        else:
            _handler = route.get('handler')
            _method = route.get('method')
            _middlewares = route.get('middlewares', [])
            _kwargs = route.get('kwargs')

            if _method != request.method:
                # если данный роут вызван с другим HTTP методом
                response.status_code = 405

            for middleware in _middlewares:
                request, response = await middleware(request, response)
            # вызов метода-обработчика роута
            # здесь не дает другим обработчикам работать
            response = await _handler(request, response)

        return response

    async def _accept_request(self, reader: StreamReader, writer: StreamWriter):
        asyncio.create_task(self._handle_request(reader, writer))

    async def _write_response(self, writer: StreamWriter, response: HttpResponse):
        writer.write(response.make_raw_response())
        await writer.drain()

    async def _handle_request(self, reader: StreamReader, writer: StreamWriter):

        try:
            logger.info(f's read: {datetime.now()}')
            raw_data = await self._read_stream(reader)
            logger.info(f'e read: {datetime.now()}')

            if raw_data == b'':
                writer.close()
                return

            request = HttpRequest(raw_data)
            logger.info(f's hand: {datetime.now()}')
            response = await asyncio.create_task(self._handle_router(request))
            logger.info(f'e hand: {datetime.now()}')

            await self._write_response(writer, response)
        except ResponseError as e:
            await self._write_response(writer, e.response)
        except Exception as e:
            logger.error(e)
        finally:
            logger.info(f'f reqs: {datetime.now()}')
            writer.close()


srv = WebServer(port=8008)


async def check_headers_middleware(req, res: HttpResponse):
    logger.warning('EMPTY middleware ')
    res.status_code = 401

    raise ResponseError(res)
    return req, res


@srv.route('/main', method=HTTPMethod.GET, middlewares=[check_headers_middleware])
async def handler(request: HttpRequest, response: HttpResponse) -> HttpResponse:
    start = datetime.now()
    await asyncio.sleep(1)
    response.json = {'result': {'start': str(start), 'end': str(datetime.now())}}
    return response


@srv.route('/signin', method=HTTPMethod.POST)
async def sign_in():
    pass


@srv.route('/send_message', method=HTTPMethod.POST)
async def send_message(req: HttpRequest, res: HttpResponse):
    chat_id = req.qs.get('chat_id')
    if not chat_id:
        raise Exception('Не указан параметр: chat_id')

    data = req.json
    data['chat_id'] = chat_id[0]

    try:
        message = ChatMessage(**data)
    except Exception:
        res.status_code = 422
        res.json = {'result': 'Не удалось провалидировать модель'}
        raise ValidateEntityError(res)

    messages_store.add_message(message)

    res.status_code = 201
    return res


@srv.route('/signup', method=HTTPMethod.POST)
async def sign_up() -> tuple[int, Optional[dict]]:

    return (202, {'result': 'welcome'})


if __name__ == '__main__':
    with open('log-config.yml', 'r') as stream:
        cfg = yaml.safe_load(stream)

    logging.config.dictConfig(cfg.get('logging'))
    asyncio.run(srv.listen())

# TODO: надо бы мидлвари прикрутить
# TODO: парсинг query-string
# TODO: надо бы парсить куки, а то как считать сессии
# TODO: Почему обработчики не вызываются конкурентно?
