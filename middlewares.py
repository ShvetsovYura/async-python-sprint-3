from exceptions import NotAuthorizedError
from http_request import HttpRequest
from http_response import HttpResponse


async def check_auth(request: HttpRequest,
                     response: HttpResponse) -> tuple[HttpRequest, HttpResponse]:

    # Да я знаю что безопасноть ни к черут =)
    # базовая - базовая проверка

    if not request._cookies:
        raise NotAuthorizedError()

    cookie_values = request._cookies.get('Cookie')
    if not cookie_values:
        raise NotAuthorizedError()

    session_value = cookie_values.value.split('=')[1]

    if not session_value:
        raise NotAuthorizedError()

    return request, response
