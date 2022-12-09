from dataclasses import dataclass
from typing import Optional


@dataclass
class Room:
    id_: str
    name: str
    owner: Optional[str] = None
    messages_in_period: int = 20
    period: float = 5
