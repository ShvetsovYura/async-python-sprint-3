import logging
from datetime import datetime, timedelta
from pathlib import Path

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

    def _get_send_user_messages_count_by_period(self, user_id: str):

        messages_in_interval = filter(
            lambda msg: msg.user_id == user_id and msg.created_at >= datetime.now() - timedelta(
                minutes=20), self.messages)
        return len(list(messages_in_interval))
