import json
from urllib.parse import ParseResult, parse_qs, urlparse

from http_consts import HTTPMethod


class HttpRequest:

    def __init__(self, raw_request: bytes):
        splited = raw_request.decode('utf-8').split('\r\n')

        self._method, self._path, self._qs, self._protocol = self._parse_meta(splited[0])
        self._headers = self._parse_headers(splited[1:-2])

        self._data = json.loads(splited[-1]) if splited[-1] else None

    @property
    def method(self):
        return self._method

    @property
    def path(self):
        """ Возвращается путь без query-string """
        return self._path

    @property
    def json(self) -> dict:
        return self._data or {}

    @property
    def qs(self):
        return self._qs

    def _parse_headers(self, headers: list[str]):
        """ Парсинг заголовков HTTP запроса """
        parsed_headers = {}
        for header in headers:
            title, value = header.split(':', 1)
            parsed_headers[title.strip()] = value.strip()
        return parsed_headers

    def _parse_meta(self, meta: str):
        """ Парсинг первой строки HTTP запроса """
        method, path, protocol = meta.split()
        _method = HTTPMethod.GET
        if method == 'POST':
            _method = HTTPMethod.POST

        parsed: ParseResult = urlparse(path)
        parsed_path = parsed.path
        parsed_qs = parse_qs(parsed.query)

        return _method, parsed_path, parsed_qs, protocol
