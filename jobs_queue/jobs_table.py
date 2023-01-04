import argparse
import datetime
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Union

import pandas as pd
import psutil

try:
    from filelock import FileLock
except ImportError:
    print(
        f"FileLock import does not exist in current env. Watch out for users accessing the queue at the same time..."
    )

from . import JOBS_TABLE_FILENAME

JOBS_TABLE_FILENAME.parent.mkdir(mode=0o774, parents=True, exist_ok=True)

lock = FileLock(f"{JOBS_TABLE_FILENAME}.lock")

from .gpu_memory import GpuManager
from .jobs import Priority, State, get_job_repr
from .user_settings import get_user_paths

__all__ = ["JOBS_TABLE_FILENAME", "JobsTable"]


def not_implemented(*args, **kwargs):
    return f"NotImplementedError: This feature is not yet implemented"


@lock
def kills(args):
    """Kill a job

    Adapted from: https://stackoverflow.com/a/62066884/20478813
    """
    id = args.id
    dry = not args.yes
    # extra kwargs from smtpserver.libclient
    user_login: str = args.extra_kwargs["user_login"]

    df = JobsTable.read()

    runing = (
        df[(df.pid != "---") & (df.user == user_login)].id.values.astype(int).tolist()
    )

    pid_list = df[df.id == id]
    pid = "---" if len(pid_list.pid) == 0 else pid_list.pid.values[0]

    if (pid == "---") or (int(id) not in runing):
        return f"Invalid job id. Expected: {runing} . Got: {id}"

    if dry:
        return f"DRY-RUN: Killing job with id={id} . If you are sure you want to kill this process use flag -y/--yes"

    try:
        parent = psutil.Process(int(pid))
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
        return f"Killed job with id={id}"
    except:  # FIXME: specify the kill error
        return f"Failed to kill job with id={id}"


def show_info(*args, **kwargs):
    pholder = " --- "
    if JOBS_TABLE_FILENAME.exists():
        mtime = datetime.datetime.fromtimestamp(JOBS_TABLE_FILENAME.stat().st_mtime)
        mode = JOBS_TABLE_FILENAME.stat().st_mode
        size = JOBS_TABLE_FILENAME.stat().st_size
    else:
        mtime = pholder
        mode = pholder
        size = pholder

    msg = f"""Queue:
  dir: {JOBS_TABLE_FILENAME.parent}
  filename: {JOBS_TABLE_FILENAME}
  exists: {JOBS_TABLE_FILENAME.exists()}
  mode: {mode}
  modified: {mtime}
  size: {size} B
"""
    return msg


class JobsTable:
    @staticmethod
    def get_empty_table() -> pd.DataFrame:
        job_cols = [
            "pid",  # None when created
            "id",
            "user",
            "command",
            "priority",
            "gpu_mem",
            "state",
            "ctime",  # Created
            "stime",  # Started
            "ftime",  # Finished
            "env_path",
            "working_dir",
        ]
        return pd.DataFrame({col: [] for col in job_cols})

    @staticmethod
    @lock
    def read() -> pd.DataFrame:
        "Read jobs table sorted by state, priority and timestamp"
        try:
            df = pd.read_csv(JOBS_TABLE_FILENAME, sep=";")
            states_order = [
                State.RUNNING.value,
                State.WAITING.value,
                State.PAUSED.value,
                State.FINISHED.value,
                State.ERROR.value,
            ]

            df["s"] = pd.Categorical(
                df["state"], states_order
            )  # State: running, waiting, finished, error
            df["p"] = pd.Categorical(
                df["priority"], sorted(Priority._value2member_map_.keys(), reverse=True)
            )  # Highest priority first
            df["ctime"] = df.ctime.apply(pd.Timestamp)  # Oldest ctime first
            df["stime"] = df.stime.apply(lambda x: x if x == "---" else pd.Timestamp(x))
            df["ftime"] = df.ftime.apply(lambda x: x if x == "---" else pd.Timestamp(x))

            # Sort by priority and Timestamp
            df.sort_values(by=["s", "p", "ctime"], inplace=True)
            df.drop(["s", "p"], axis=1, inplace=True)  # Drop state and priority helper

            return df
        except FileNotFoundError:
            return JobsTable.get_empty_table()

    @staticmethod
    @lock
    def write(df: pd.DataFrame) -> None:
        df.to_csv(JOBS_TABLE_FILENAME, sep=";", index=None)
        # Read, Write, Execute permissions so other users can change the files
        try:
            JOBS_TABLE_FILENAME.chmod(0o774)
        except PermissionError:
            ...

    # ================================================================= #
    # ======================== USER INTERFACE ========================= #
    # ================================================================= #

    @staticmethod
    @lock
    def add(args: argparse.Namespace):
        command: str = args.command
        priority: Union[Priority, str] = args.priority
        gpu_mem: float = args.gpu_mem
        verbose: int = args.verbose
        envname: str = args.envname
        working_dir: str = args.working_dir
        # extra kwargs from smtpserver.libclient
        user_login: str = args.extra_kwargs["user_login"]

        msg = ""

        upaths = get_user_paths(user_login, envname)

        data = dict(
            pid="---",
            id=JobsTable.get_new_valid_id(),
            user=user_login,
            command=" ".join(command),
            priority=Priority.get_valid(priority).value,
            gpu_mem=int(gpu_mem),
            state=State.PAUSED.value,
            ctime=datetime.datetime.now(),
            stime="---",
            ftime="---",
            env_path=upaths["env_path"],
            working_dir=str(Path(working_dir).resolve())
            if working_dir is not None
            else upaths["working_dir"],
        )

        GpuManager.update()
        if not any(
            gpu_mem <= single_gpu for single_gpu in GpuManager.TOTAL_single.values()
        ):
            msg += "WARNING: 'gpu_mem' exceeds any single gpu memory. Using multiple gpus...\n"

        new_row = pd.DataFrame(data, index=[0])

        new_row["ctime"] = new_row.ctime.apply(pd.Timestamp)

        msg += f"Adding {get_job_repr(new_row.values, lvl=verbose)} ..."

        JobsTable.write(JobsTable.read().append(new_row))

        return msg

    @staticmethod
    @lock
    def update(args: argparse.Namespace):
        id: int = args.id
        attr: str = args.attr
        new_value: str = args.new_value
        verbose: int = args.verbose
        # extra kwargs from smtpserver.libclient
        user_login: str = args.extra_kwargs["user_login"]

        df = JobsTable.read()

        if id not in JobsTable.get_jobs_ids():
            return f"The id={id} is not a valid job id. Expected: {JobsTable.get_jobs_ids()}"

        df = JobsTable.read()
        if df[(df.id == id) & (df.user == user_login)].empty:
            return f"User {user_login} not allowed to update job. Job belongs to {df[(df.id == id)].user} "

        if attr == "priority":
            new_value = Priority.get_valid(new_value).value
        elif attr == "command":
            new_value = new_value
        elif attr == "gpu_mem":
            new_value = float(new_value)
        else:
            return f"Job has no attribute/can't update attribute={attr}"

        msg = f"Updating {get_job_repr(df.loc[df.id == id].values, lvl=verbose)} . {attr}={df.loc[df.id == id][attr].values[0]} -> {attr}={new_value} ..."

        df.loc[df.id == id, attr] = new_value

        JobsTable.write(df)

        return msg

    @staticmethod
    @lock
    def pause(args: argparse.Namespace):
        op: str = args.op
        verbose: int = args.verbose
        if op not in ["ids", "priority", "all"]:
            return f"Expected args.op in ['ids', 'priority', 'all'] . Got: {op}"

        df = JobsTable.read()
        ids = df[df["state"] == State.WAITING.value].id.values  # op = 'all'

        if op == "ids":
            ids = list(filter(lambda id: id in ids, args.ids))
        elif op == "priority":
            ids = df[
                (df["state"] == State.WAITING.value)
                & (df["priority"] == Priority.get_valid(args.priority).value)
            ].id.values

        [JobsTable.set_job_state(id, state=State.PAUSED) for id in ids]

        return f"Pausing {op}: {ids}"

    @staticmethod
    @lock
    def unpause(args: argparse.Namespace):
        op: str = args.op
        verbose: int = args.verbose
        if op not in ["ids", "priority", "all"]:
            return f"Expected args.op in ['ids', 'priority', 'all'] . Got: {op}"
        df = JobsTable.read()
        ids = df[df["state"] == State.PAUSED.value].id.values  # pause = 'all'

        if op == "ids":
            ids = list(filter(lambda id: id in ids, args.ids))
        elif op == "priority":
            ids = df[
                (df["state"] == State.PAUSED.value)
                & (df["priority"] == Priority.get_valid(args.priority).value)
            ].id.values

        [JobsTable.set_job_state(id, state=State.WAITING) for id in ids]

        return f"Resuming {op}: {ids}"

    @staticmethod
    @lock
    def remove(args: argparse.Namespace):
        ids: List[int] = args.ids
        verbose: int = args.verbose
        # extra kwargs from smtpserver.libclient
        user_login: str = args.extra_kwargs["user_login"]

        df = JobsTable.read()

        new_df = df[~((df.id.isin(ids)) & (df.user == user_login))]

        msg = f"Removing {df.shape[0] - new_df.shape[0]} jobs ..."

        JobsTable.write(new_df)

        return msg

    @staticmethod
    def show(args: argparse.Namespace):
        verbose: int = args.verbose
        df = JobsTable.read()

        if "id" in args and args.id is not None:
            if args.id in JobsTable.get_jobs_ids():
                return get_job_repr(df.loc[df.id == args.id].values, lvl=verbose)

            return f"Job with id={args.id} does not exist. Expected: {JobsTable.get_jobs_ids()}"

        elif "state" in args and args.state is not None:
            jobs = df[df.state == State.get_valid(args.state).value]
            str_ = "Jobs:\n"
            for job in jobs.iterrows():
                str_ += f"  {get_job_repr([job[1].values], lvl=verbose)}\n"
            return str_

        else:
            str_ = "Jobs:\n"
            for job in df.iterrows():
                str_ += f"  {get_job_repr([job[1].values], lvl=verbose)}\n"
            return str_

    @staticmethod
    @lock
    def clear(args: argparse.Namespace):
        yes: bool = args.yes

        if not yes:
            return "Aborting clear command ! If you are sure you want to clear all jobs run the same command with the flag -y or --yes"

        JobsTable.write(JobsTable.get_empty_table())
        return "Clearing all jobs..."

    @staticmethod
    @lock
    def clear_state(args: argparse.Namespace):
        state: str = args.state

        df = JobsTable.read()

        msg = f"Clearing {df[df.state == State.get_valid(state).value ].shape[0]} jobs ..."

        df_wo_state = df[df.state != State.get_valid(state).value]

        JobsTable.write(df_wo_state)

        return msg

    # ================================================================= #
    # ================================================================= #
    # ================================================================= #

    @staticmethod
    @lock
    def set_job_state(id: int, state: Union[State, str]):

        if id not in JobsTable.get_jobs_ids():
            raise ValueError(
                f"The id={id} is not a valid job id. Expected: {JobsTable.get_jobs_ids()}"
            )

        df = JobsTable.read()
        df.loc[df.id == id, "state"] = State.get_valid(state).value

        JobsTable.write(df)

    @staticmethod
    @lock
    def update_job(id: int, col: str, value: Any):
        df = JobsTable.read()
        assert col in df.columns, f"Invalid column: {col}"

        if id not in JobsTable.get_jobs_ids():
            raise ValueError(
                f"The id={id} is not a valid job id. Expected: {JobsTable.get_jobs_ids()}"
            )

        df.loc[df.id == id, col] = value

        JobsTable.write(df)

    # ================================================================= #
    @staticmethod
    @lock
    def get_next_job() -> Union[pd.DataFrame, None]:
        df = JobsTable.read()

        if df.empty:
            # No jobs
            return

        waiting_jobs = df[df.state == State.WAITING.value]
        if waiting_jobs.empty:
            # No pending jobs
            return

        job = waiting_jobs.head(1)

        # Update job state
        job.at[job.index[0], "state"] = State.RUNNING.value

        # Update table
        df[df.id == job.id.values[0]] = job
        JobsTable.write(df)

        return job

    @staticmethod
    def get_jobs_ids() -> List[int]:
        df = JobsTable.read()
        return df.id.values

    @staticmethod
    def get_new_valid_id() -> int:
        """Get a new id that does not exist yet"""
        valid_id = 0
        while valid_id in JobsTable.get_jobs_ids():
            valid_id += 1
        return valid_id

    @staticmethod
    def get_job(id: int) -> Union[pd.DataFrame, None]:
        if id not in JobsTable.get_jobs_ids():
            return

        df = JobsTable.read()
        job = df[df.id == id]
        return job


if __name__ == "__main__":

    @dataclass
    class AddArgs:
        command: str
        priority: str
        gpu_mem: float
        verbose: int = 1

    @dataclass
    class UpdateArgs:
        id: int
        attr: str
        new_value: str
        verbose: int = 1

    @dataclass
    class RemoveArgs:
        ids: List[int]
        verbose: int = 1

    @dataclass
    class ShowArgs:
        id: int
        verbose: int = 1

    @dataclass
    class ClearArgs:
        yes: bool

    @dataclass
    class ClearStateArgs:
        state: str
