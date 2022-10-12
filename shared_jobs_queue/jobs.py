import datetime
import os
from enum import Enum, auto
from pathlib import Path


class Priority(Enum):
    LOW = auto()
    MEDIUM = NORMAL = auto()
    HIGH = auto()
    URGENT = auto()



class Job:
    verbose_lvl:int
    def __init__(self, priority: Priority, command: str, _id: int, verbose_lvl:int=1) -> None:
        self.priority = priority
        self.command = command
        self._id = _id
        self.user = os.getlogin()
        self.timestamp = datetime.datetime.now()
        self.verbose_lvl=verbose_lvl

    def __lt__(self, other):
        # Sort by priority and timestamp
        return (
            self.priority.value < other.priority.value
            and self.timestamp < other.timestamp
        )

    def __str__(self) -> str:
        return self._str_lvl_(self.verbose_lvl)
    
    def _str_lvl_(self, lvl):
        if lvl <= 0:
            return self._str_0
        elif lvl == 1:
            return self._str_1
        elif lvl == 2:
            return self._str_2
        else:
            return self._str_3

    @property
    def _str_0(self):
        return f'{self.__class__.__name__}(id={self._id}, priority={self.priority.value}, timestamp={self.timestamp:%m/%d-%H:%M})'
    @property
    def _str_1(self):
        return f'{self.__class__.__name__}(id={self._id}, command="{self.command[:10]} [...]", priority={self.priority.name}, timestamp={self.timestamp:%m/%d-%H:%M})'
    @property
    def _str_2(self):
        return f'{self.__class__.__name__}(id={self._id}, user={self.user}, command="{self.command[:80]} [...]", priority={self.priority.name}, timestamp={self.timestamp:%m/%d/%Y-%H:%M:%S})'
    @property
    def _str_3(self):
        return f'{self.__class__.__name__}(id={self._id}, user={self.user}, command="{self.command}", priority={self.priority.name}, timestamp={self.timestamp})'
    
    
    __repr__ = __str__


# ENDFILE
