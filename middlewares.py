from exceptions import NotAuthorizedError
from http_request import HttpRequest
from http_response import HttpResponse


async def check_auth(request: HttpRequest,
                     response: HttpResponse) -> tuple[HttpRequest, HttpResponse]:

    # Да я знаю что безопасноть ни к черут =)
    # базовая - базовая проверка

    if not request._cookies:
        raise NotAuthorizedError()

    session_value = request._cookies.get('Cookie').value
    if not session_value:
        raise NotAuthorizedError()

    return request, response
