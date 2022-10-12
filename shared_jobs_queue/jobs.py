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
        cmd_str=self.command[:lvl*30]
        if len(cmd_str) != len(self.command):
            cmd_str+='[...]'
        if lvl < 0:
            return self._full_str_
        elif lvl == 0:
            return  f'{self.__class__.__name__}(id={self._id}, priority={self.priority.value}, timestamp={self.timestamp:%m/%d-%H:%M})'
        elif lvl == 1:
            return  f'{self.__class__.__name__}(id={self._id}, command="{cmd_str}", priority={self.priority.name}, timestamp={self.timestamp:%m/%d-%H:%M})'
        elif lvl == 2:
            return  f'{self.__class__.__name__}(id={self._id}, user={self.user}, command="{cmd_str}", priority={self.priority.name}, timestamp={self.timestamp:%m/%d/%Y-%H:%M:%S})'
        else:
            return f'{self.__class__.__name__}(id={self._id}, user={self.user}, command="{cmd_str}", priority={self.priority.name}, timestamp={self.timestamp})'

    @property
    def _full_str_(self):
        return f'{self.__class__.__name__}(id={self._id}, user={self.user}, command="{self.command}", priority={self.priority.name}, timestamp={self.timestamp})'
    
    
    __repr__ = __str__


# ENDFILE
