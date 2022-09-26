import datetime
import os
from enum import Enum, auto


class Priority(Enum):
    LOW = auto()
    MEDIUM = NORMAL = auto()
    HIGH = auto()
    URGENT = auto()



class Job:
    def __init__(self, priority: Priority, command: str, _id: int) -> None:
        self.priority = priority
        self.command = command
        self._id = _id
        self.user = os.getlogin()
        self.timestamp = datetime.datetime.now()

    def __lt__(self, other):
        # Sort by priority and timestamp
        return (
            self.priority.value < other.priority.value
            and self.timestamp < other.timestamp
        )

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(_id={self._id}, user={self.user}, command="{self.command}", priority={self.priority}, timestamp={self.timestamp})'

    __repr__ = __str__


# ENDFILE
