from enum import Enum

status_codes = {
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not found',
    405: 'Method Not Allowed',
    422: 'Unprocessable Entity',
    423: 'Locked',
    500: 'Internal Server Error',
}


class HTTPMethod(Enum):
    GET = 'GET'
    POST = 'POST'
