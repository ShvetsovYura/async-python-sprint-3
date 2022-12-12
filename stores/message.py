import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Union


def get_uuid() -> str:
    return str(uuid.uuid4())


@dataclass
class ChatMessage:

    message: str
    user_id: str
    chat_id: str
    read_users: list[str] = field(default_factory=list)

    parent_id: Optional[str] = None
    id_: str = field(default_factory=get_uuid)
    delivery_at: Union[datetime, None] = None
    created_at: datetime = field(default_factory=datetime.now)

