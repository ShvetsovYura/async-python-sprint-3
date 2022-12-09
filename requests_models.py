from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SignInRequestModel:
    login: str
    password: str

@dataclass
class SingUpRequestModel(SignInRequestModel):
    name: str

@dataclass
class MessageRequestModel:
    user_id: str
    chat_id: str
    parent_id: str
    message: str

    delivery_at: Optional[datetime]
