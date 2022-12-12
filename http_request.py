from ctypes import Union
import json
from http import cookies
from typing import Optional
from urllib.parse import ParseResult, parse_qs, urlparse

from http_consts import HTTPMethod


class HttpRequest:

    def __init__(self, raw_request: bytes):
        splited = raw_request.decode('utf-8').split('\r\n')

        self._method, self._path, self._qs, self._protocol = self._parse_meta(splited[0])
        self._headers = self._parse_headers(splited[1:-2])

        self._data = json.loads(splited[-1]) if splited[-1] else None

        self._cookies: Optional[cookies.SimpleCookie] = None
        cookie_header = list(filter(lambda c: c.get('Cookie'), self._headers))

        if cookie_header:
            self._cookies = self._parse_cookie(cookie_header[0])

    @property
    def method(self):
        return self._method

    @property
    def path(self):
        """ Возвращается путь без query-string """
        return self._path

    @property
    def json(self):
        return self._data

    def get_parsed_cookies(self) -> dict:
        parsed_cookies = {}
        if not self._cookies:
            return {}

        for _, morsel in self._cookies.items():
            if morsel.value:
                splitted_values = morsel.value.split('=')
                parsed_cookies[splitted_values[0]] = splitted_values[1]

        return parsed_cookies

    @property
    def qs(self):
        return self._qs

    def _parse_headers(self, headers: list[str]) -> list[dict[str, str]]:
        """ Парсинг заголовков HTTP запроса """

        parsed_headers: list[dict[str, str]] = []
        for header in headers:
            title, value = header.split(':', 1)
            parsed_headers.append({title.strip(): value.strip()})
        return parsed_headers

    def _parse_cookie(self, raw_cookie: dict):
        parsed_cookies = cookies.SimpleCookie(raw_cookie)
        return parsed_cookies

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
