import json
from http_consts import status_codes


class HttpResponse:

    def __init__(self) -> None:
        self._status_code = 200
        self._headers = {}
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
    def status_code(self, value: int):
        self._status_code = value

    @headers.setter
    def headers(self, value: dict):
        self._headers = value

    @json.setter
    def json(self, value: dict):
        self._json = value

    def make_response(self) -> str:

        _headers, _body = None, None

        if self.headers:
            _headers = '\r\n'.join([f'{key}: {value}' for key, value in self.headers.items()])

        if self.json:
            _body = json.dumps(self.json)

        raw_response = 'HTTP/1.1 {status} {status_str}\r\n{headers}\r\n\r\n{body}'.format(
            status=self.status_code,
            status_str=status_codes[self.status_code],
            headers=_headers,
            body=_body)

        return raw_response

    def make_raw_response(self) -> bytes:
        return self.make_response().encode('utf-8')
