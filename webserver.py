import asyncio
import logging
import logging.config
from asyncio.streams import StreamReader, StreamWriter
from http import HTTPStatus
from typing import Callable, Optional, TypedDict

from exceptions import BadRequestDataError, NotAuthorizedError, ResponseError
from http_consts import HTTPMethod
from http_request import HttpRequest
from http_response import HttpResponse
from stores.data_manager import DataManager

logger = logging.getLogger(__name__)

mgr = DataManager()


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

        # Задачи периодического сохранения информации в файлы
        asyncio.create_task(mgr.messages_store.dump_records())
        asyncio.create_task(mgr.users_store.dump_records())
        asyncio.create_task(mgr.rooms_store.dump_records())
        asyncio.create_task(mgr.run_remove_messages_older_than())

        await asyncio.create_task(self._start_server())

    def route(self,
              url: str,
              method: HTTPMethod,
              middlewares: Optional[list[Callable]] = None,
              **kwargs):
        """ Декоратор для связывания роута и обработчика """

        def _route(_handler: Callable) -> Callable:
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
        response.add_header({'Content-Type': 'application/json; charset=utf-8'})
        response.add_header({'x-powered-by': 'simple-json-server'})

        if not route:
            # если не найдено роута
            response.status_code = HTTPStatus.NOT_FOUND
        else:
            _handler = route.get('handler')
            _method = route.get('method')
            _middlewares = route.get('middlewares', [])
            # _kwargs = route.get('kwargs') # noqa E800

            if _method != request.method:
                # если данный роут вызван с другим HTTP методом
                response.status_code = HTTPStatus.METHOD_NOT_ALLOWED

            for middleware in _middlewares:
                request, response = await middleware(request, response)

            # вызов метода-обработчика роута
            # здесь не дает другим обработчикам работать
            response = await _handler(request, response)

        return response

    async def _accept_request(self, reader: StreamReader, writer: StreamWriter):
        asyncio.create_task(self._handle_request(reader, writer))

    async def _write_response(self,
                              writer: StreamWriter,
                              response: HttpResponse,
                              status_code: Optional[HTTPStatus] = None):
        if status_code:
            response.status_code = status_code
        writer.write(response.make_raw_response())
        await writer.drain()

    async def _handle_request(self, reader: StreamReader, writer: StreamWriter) -> None:
        """ Обработка входящего запроса от клиента """

        response = HttpResponse()

        try:
            raw_data = await self._read_stream(reader)

            if raw_data == b'':
                writer.close()
                return

            request = HttpRequest(raw_data)
            response = await self._handle_router(request)

            await self._write_response(writer, response)
        except BadRequestDataError:
            await self._write_response(writer, response, HTTPStatus.UNPROCESSABLE_ENTITY)
        except NotAuthorizedError:
            await self._write_response(writer, response, HTTPStatus.UNAUTHORIZED)
        except ResponseError as e:
            await self._write_response(writer, e.response)
        except Exception as e:    # noqa B902
            logger.error(e)
        finally:
            writer.close()
