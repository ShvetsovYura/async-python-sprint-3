import asyncio
import dataclasses
import logging
import logging.config
from datetime import datetime

import yaml

from exceptions import BadRequestDataError, ResponseError, UserNotFoundError
from http_consts import HTTPMethod
from http_request import HttpRequest
from http_response import HttpResponse
from middlewares import check_auth
from requests_models import (MessageRequestModel, SignInRequestModel,
                             SingUpRequestModel)
from stores.data_manager import DataManager
from stores.message import ChatMessage
from webserver import WebServer

logger = logging.getLogger(__name__)

mgr = DataManager()

srv = WebServer(port=8008)


async def check_headers_middleware(req, res: HttpResponse):
    logger.warning('EMPTY middleware ')
    res.status_code = 401

    raise ResponseError(res)
    return req, res


@srv.route('/main', method=HTTPMethod.GET, middlewares=[check_auth])
async def handler(request: HttpRequest, response: HttpResponse) -> HttpResponse:
    start = datetime.now()
    await asyncio.sleep(1)
    response.json = {'result': {'start': str(start), 'end': str(datetime.now())}}
    response.set_cookie('pipa', 'oh-no')
    return response


@srv.route('/signin', method=HTTPMethod.POST)
async def sign_in(request: HttpRequest, response: HttpResponse):
    try:
        user_req = SignInRequestModel(**request.json)
    except TypeError:
        raise BadRequestDataError

    users_ = mgr.users_store.get_users_by_login(user_req.login)
    if not users_:
        raise UserNotFoundError
    user_ = users_[0]
    user_.check_login_password(user_req.login, user_req.password)
    response.set_cookie('session', user_.id_)

    response.status_code = 202
    return response


@srv.route('/send_message', method=HTTPMethod.POST, middlewares=[check_auth])
async def send_message(req: HttpRequest, res: HttpResponse):

    chat_id = req.qs.get('chat_id')
    if not chat_id:
        raise BadRequestDataError

    try:
        message = MessageRequestModel(chat_id=chat_id[0], **req.json)
    except TypeError:
        raise BadRequestDataError

    mgr.add_message(ChatMessage(**dataclasses.asdict(message)))

    res.status_code = 201
    return res


@srv.route('/signup', method=HTTPMethod.POST)
async def sign_up(request: HttpRequest, response: HttpResponse):

    try:
        request_model = SingUpRequestModel(**request.json)
    except TypeError:
        raise BadRequestDataError

    mgr.add_user(login=request_model.login, name=request_model.name, pwd=request_model.password)

    response.status_code = 201
    return response


if __name__ == '__main__':
    with open('log-config.yml', 'r') as stream:
        cfg = yaml.safe_load(stream)

    logging.config.dictConfig(cfg.get('logging'))
    asyncio.run(srv.listen())

# TODO: Почему обработчики не вызываются конкурентно?
# TODO: Наверно нужно было делать на web-сокетах, но уже слишком поздно переделывать
