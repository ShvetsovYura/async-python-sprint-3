class ResponseError(Exception):

    def __init__(self, response, *args) -> None:
        super().__init__(*args)
        self.response = response


class ValidateEntityError(Exception):

    def __init__(self, response, *args) -> None:
        super().__init__(*args)
        self.response = response


class OverflowSendMessagesUserBlocked(Exception):
    pass


class NotAuthorizedError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class BadRequestDataError(Exception):
    pass


class RoomNameAlreadyExistsError(Exception):
    pass


class UserLoginAlreadyExists(Exception):
    pass
