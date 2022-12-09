from exceptions import NotAuthorizedError
from http_request import HttpRequest
from http_response import HttpResponse


async def check_auth(request: HttpRequest,
                     response: HttpResponse) -> tuple[HttpRequest, HttpResponse]:
    if not request._cookies:
        raise NotAuthorizedError()

    session_cookie = request._cookies.get('session')
    if not session_cookie:
        raise NotAuthorizedError()

    return request, response
