from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Room:
    id_: str
    name: str
    owner: Optional[str] = None
    messages_in_period: int = 20
    period: float = 5
    users: list[str] = field(default_factory=list)
