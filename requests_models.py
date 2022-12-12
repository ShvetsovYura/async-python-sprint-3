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
    message: str

    parent_id: Optional[str] = None
    delivery_at: Optional[datetime] = None
