import logging
from pathlib import Path
from typing import Optional

from stores.base_store import BaseStore
from stores.message import ChatMessage

logger = logging.getLogger(__name__)


class MessagesStore(BaseStore):

    def __init__(self) -> None:
        super().__init__(
            Path(__file__).resolve().parent.parent / 'data/messages.json', ChatMessage)

    @property
    def messages(self) -> list[ChatMessage]:
        return self.records

    def get_messages(self, limit: Optional[int] = None):
        if limit:
            return self.messages[-limit:]
        return self.messages

    def _set_messages(self, messages: list[ChatMessage]):
        self._records = messages
