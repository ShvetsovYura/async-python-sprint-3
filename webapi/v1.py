import dataclasses
import logging
from http import HTTPStatus

from exceptions import BadRequestDataError, UserNotFoundError
from http_consts import HTTPMethod
from http_request import HttpRequest
from http_response import HttpResponse
from middlewares import check_auth
from requests_models import (ComplaintUserRequestModel, MessageRequestModel, RoomRequestModel,
                             SignInRequestModel, SingUpRequestModel)
from stores.data_manager import DataManager
from stores.message import ChatMessage
from stores.messages_store import MessagesStore
from stores.rooms_store import RoomsStore
from stores.users_store import UsersStore
from webserver import WebServer

mgr = DataManager(users_store=UsersStore(),
                  rooms_store=RoomsStore(),
                  messages_store=MessagesStore())

logger = logging.getLogger(__name__)

webapp = WebServer(data_manager=mgr)


@webapp.route('/health', method=HTTPMethod.GET)
async def health(request: HttpRequest, response: HttpResponse):
    response.json = [{'status': 'UP'}]

    response.status_code = HTTPStatus.OK
    return response


@webapp.route('/signin', method=HTTPMethod.POST)
async def sign_in(request: HttpRequest, response: HttpResponse):
    try:
        user_req = SignInRequestModel(**request.json)    # type: ignore
    except TypeError:
        raise BadRequestDataError

    user_ = mgr.users_store.get_user_by_login(user_req.login)
    if not user_:
        raise UserNotFoundError

    user_.check_login_password(user_req.login, user_req.password)
    response.set_cookie('session', user_.id_)

    response.status_code = HTTPStatus.ACCEPTED
    return response


@webapp.route('/send_message', method=HTTPMethod.POST, middlewares=[check_auth])
async def send_message(request: HttpRequest, response: HttpResponse):

    chat_id = request.qs.get('chat_id')
    if not chat_id:
        raise BadRequestDataError
    cookies_ = request.get_parsed_cookies()

    user_id = cookies_.get('session')
    if not user_id:
        raise BadRequestDataError

    try:
        message = MessageRequestModel(chat_id=chat_id[0], user_id=user_id,
                                      **request.json)    # type: ignore
    except TypeError as e:
        logger.exception(e)
        raise BadRequestDataError

    mgr.add_message(ChatMessage(**dataclasses.asdict(message)))

    response.status_code = HTTPStatus.CREATED
    return response


@webapp.route('/signup', method=HTTPMethod.POST)
async def sign_up(request: HttpRequest, response: HttpResponse):

    try:
        request_model = SingUpRequestModel(**request.json)    # type: ignore
    except TypeError:
        raise BadRequestDataError

    mgr.create_user(login=request_model.login, name=request_model.name, pwd=request_model.password)

    messages = mgr.messages_store.get_messages(20)

    response.status_code = HTTPStatus.CREATED
    return messages


@webapp.route('/get_unread_messages', method=HTTPMethod.GET, middlewares=[check_auth])
async def get_unread_messages(request: HttpRequest, response: HttpResponse):

    cookies_ = request.get_parsed_cookies()
    user_id_ = cookies_.get('session')
    if not user_id_:
        raise BadRequestDataError()

    messages = mgr.get_unread_user_messages(user_id=user_id_)

    response.status_code = HTTPStatus.OK
    response.json = [dataclasses.asdict(message) for message in messages]

    return response


@webapp.route('/mark_messages_as_read', method=HTTPMethod.POST, middlewares=[check_auth])
async def set_read_messages(request: HttpRequest, response: HttpResponse):
    cookies_ = request.get_parsed_cookies()

    mgr.set_read_messages_by_user(*[request.json, cookies_.get('session')])

    response.status_code = HTTPStatus.OK
    return response


@webapp.route('/leave_room', method=HTTPMethod.POST, middlewares=[check_auth])
async def user_leave_room(request: HttpRequest, respose: HttpResponse):
    cookies_ = request.get_parsed_cookies()

    try:
        model = RoomRequestModel(**request.json)    # type: ignore
    except TypeError:
        raise BadRequestDataError

    mgr.remove_user_from_chat(cookies_.get('session', ''), model.chat_id)


@webapp.route('/complaint', method=HTTPMethod.POST, middlewares=[check_auth])
async def complaint_to_user(request: HttpRequest, response: HttpResponse):

    try:
        model = ComplaintUserRequestModel(**request.json)    # type: ignore
    except TypeError:
        raise BadRequestDataError

    user = mgr.users_store.get_user_by_id(model.user_id)

    user.set_complaint()

    response.status_code = HTTPStatus.CREATED
    return response
