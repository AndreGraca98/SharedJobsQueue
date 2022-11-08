import datetime
import os
from enum import Enum, auto
from typing import Union


class Priority(Enum):
    LOW = auto()
    MEDIUM = NORMAL = auto()
    HIGH = auto()
    URGENT = auto()


class State(Enum):
    ERROR = -1
    WAITING = 0
    RUNNING = 1
    FINISHED = 2


class Job:
    def __init__(
        self,
        priority: int,
        command: str,
        needed_gpu_mem: int,
        id: int,
        verbose_lvl: int,
    ) -> None:

        self.priority = priority
        self.command = command
        self.needed_gpu_mem = needed_gpu_mem
        self.id = id
        self.verbose_lvl = verbose_lvl

        self.user = os.getlogin()
        self.timestamp = datetime.datetime.now()
        self.state = State.WAITING

    def __lt__(self, other):
        return (self.priority.value < other.priority.value) or (
            self.priority.value == other.priority.value
            and self.timestamp > other.timestamp
        )

    def __gt__(self, other):
        return (self.priority.value > other.priority.value) or (
            self.priority.value == other.priority.value
            and self.timestamp < other.timestamp
        )

    def update_state(self) -> None:
        # next state
        self.state = State(self.state.value + 1)

    def set_state(self, state: Union[int, str]) -> None:
        if isinstance(state, int):
            self.state = State(state)
        elif isinstance(state, str):
            self.state = State[state]
        else:
            raise TypeError(f"Expected state type to be str or int. Got: {type(state)}")

    def __str__(self) -> str:
        return self._str_lvl_(self.verbose_lvl)

    def _str_lvl_(self, lvl):
        cmd_str = self.command[: lvl * 30]
        if len(cmd_str) != len(self.command):
            cmd_str += "[...]"
        if lvl < 0:
            return self._full_str_
        elif lvl == 0:
            return f"{self.__class__.__name__}(id={self.id}, priority={self.priority.value}, state={self.state.value}, timestamp={self.timestamp:%m/%d-%H:%M})"
        elif lvl == 1:
            return f'{self.__class__.__name__}(id={self.id}, command="{cmd_str}", priority={self.priority.name}, gpu_mem={self.needed_gpu_mem}, state={self.state.name}, timestamp={self.timestamp:%m/%d-%H:%M})'
        elif lvl == 2:
            return f'{self.__class__.__name__}(id={self.id}, user={self.user}, command="{cmd_str}", priority={self.priority.name}, gpu_mem={self.needed_gpu_mem}, state={self.state.name}, timestamp={self.timestamp:%m/%d/%Y-%H:%M:%S})'
        else:
            return f'{self.__class__.__name__}(id={self.id}, user={self.user}, command="{cmd_str}", priority={self.priority.name}, gpu_mem={self.needed_gpu_mem}, state={self.state.name}, timestamp={self.timestamp})'

    @property
    def _full_str_(self):
        return f'{self.__class__.__name__}(id={self.id}, user={self.user}, command="{self.command}", priority={self.priority.name}, gpu_mem={self.needed_gpu_mem}, state={self.state.name}, timestamp={self.timestamp})'

    __repr__ = __str__


# ENDFILE
