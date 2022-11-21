from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, Union


class Priority(ABC):
    "Job Priority abstract class"

    @abstractmethod
    def get_valid():
        ...


class Priority(Enum):
    "Job Priority"
    LOW = 1
    MEDIUM = NORMAL = 2
    HIGH = 3
    URGENT = 4

    def get_valid(priority: Union[Priority, str]) -> Priority:
        if isinstance(priority, Priority):
            return priority

        if isinstance(priority, str) and priority.isdecimal():
            return Priority(int(priority))

        if isinstance(priority, str):
            return Priority[priority.upper()]

        raise TypeError(
            f"Got wrong priority type. Excpected: {Priority} or {str}. Got: {type(priority)}"
        )


class State(ABC):
    "Job State abstract class"

    @abstractmethod
    def get_valid():
        ...


class State(Enum):
    "Job State"
    ERROR = -1
    WAITING = 0
    RUNNING = PROCESSING = 1
    FINISHED = DONE = 2

    def get_valid(state: Union[State, str]) -> State:
        if isinstance(state, State):
            return state

        if isinstance(state, str) and state.lstrip("-").isdecimal():
            return State(int(state))

        if isinstance(state, str):
            return State[state.upper()]

        raise TypeError(
            f"Got wrong state type. Excpected: {State} or {str}. Got: {type(state)}"
        )


def get_job_repr(row_values: List[Any], lvl: int = 1) -> str:
    id, user, cmd, priority, gpu_mem, state, timestamp = row_values[0]
    state = State(state)
    priority = Priority(priority)

    cmd_str = cmd[: lvl * 30]

    if len(cmd_str) != len(cmd):
        cmd_str += "[...]"
    if lvl < 0:
        return f'Job(id={int(id)}, user={user}, command="{cmd}", priority={priority.name}, gpu_mem={gpu_mem}, state={state.name}, timestamp={timestamp})'
    elif lvl == 0:
        return f"Job(id={int(id)}, priority={priority.value}, state={state.value}, timestamp={timestamp:%m/%d-%H:%M})"
    elif lvl == 1:
        return f'Job(id={int(id)}, command="{cmd_str}", priority={priority.name}, gpu_mem={gpu_mem}, state={state.name}, timestamp={timestamp:%m/%d-%H:%M})'
    elif lvl == 2:
        return f'Job(id={int(id)}, user={user}, command="{cmd_str}", priority={priority.name}, gpu_mem={gpu_mem}, state={state.name}, timestamp={timestamp:%m/%d/%Y-%H:%M:%S})'
    else:
        return f'Job(id={int(id)}, user={user}, command="{cmd_str}", priority={priority.name}, gpu_mem={gpu_mem}, state={state.name}, timestamp={timestamp})'


# ENDFILE
