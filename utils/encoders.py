import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID


class EnhancedJsonEncoder(json.JSONEncoder):

    def default(self, serialized_object: Any) -> Any:

        serialized_types = {
            datetime: lambda: serialized_object.strftime('%Y-%m-%d %H:%M:%S'),
            date: lambda: serialized_object.strftime('%Y-%m-%d'),
            Decimal: lambda: str(serialized_object),
            Enum: lambda: serialized_object.name,
            timedelta: lambda: serialized_object.total_seconds(),
            UUID: lambda: str(serialized_object),
        }

        for _type in serialized_types:
            if isinstance(serialized_object, _type):
                return serialized_types[_type]()
        return super().default(serialized_object)
