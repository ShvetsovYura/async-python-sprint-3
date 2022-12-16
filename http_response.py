import json
import logging
from datetime import datetime, timedelta
from http import HTTPStatus, cookies
from typing import Union

logger = logging.getLogger(__name__)


class HttpResponse:

    def __init__(self) -> None:
        self._status_code = HTTPStatus.OK
        self._headers: list[str] = []
        self._json = None

    @property
    def status_code(self):
        return self._status_code

    @property
    def headers(self):
        return self._headers

    @property
    def json(self):
        return self._json

    @status_code.setter
    def status_code(self, value: HTTPStatus):
        self._status_code = value

    def add_header(self, header: dict[str, str]):
        for key, value in header.items():
            self.headers.append(f'{key}:{value}')

    def set_cookie(self,
                   key: str,
                   value: str,
                   http_only: bool = True,
                   expires: Union[str, datetime, timedelta] = 'session'):
        cookie_ = cookies.SimpleCookie()
        cookie_[key] = value

        # Определение, как было установлено время жизни кук
        if isinstance(expires, datetime):
            cookie_[key]['expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S')
        elif isinstance(expires, timedelta):
            cookie_[key]['max-age'] = int(expires.total_seconds())
        else:
            cookie_[key]['expires'] = expires

        cookie_[key]['httponly'] = http_only

        self._headers.append(str(cookie_) + ';')

    @json.setter
    def json(self, value: Union[dict, list]):
        self._json = value

    def make_response(self) -> str:

        _headers, _body = None, None

        if self.headers:
            _headers = '\r\n'.join(self._headers)

        if self.json is not None:
            _body = json.dumps(self.json)

        raw_response = 'HTTP/1.1 {status} {status_str}\r\n{headers}\r\n\r\n{body}'.format(
            status=self.status_code,
            status_str=str(self.status_code),
            headers=_headers,
            body=_body)

        return raw_response

    def make_raw_response(self) -> bytes:
        return self.make_response().encode('utf-8')
