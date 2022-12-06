import argparse
import datetime
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Union

import pandas as pd
from filelock import FileLock

try:
    from gpu_memory import GpuManager
    from jobs import Priority, State, get_job_repr
except ModuleNotFoundError:
    from .gpu_memory import GpuManager
    from .jobs import Priority, State, get_job_repr

__all__ = ["JOBS_TABLE_FILENAME", "JobsTable"]


JOBS_TABLE_FILENAME = Path("/var/tmp/jobs_queue/jobs_table.csv")
JOBS_TABLE_FILENAME.parent.mkdir(parents=True, exist_ok=True)


lock = FileLock(f"{JOBS_TABLE_FILENAME}.lock")
# Path(f"{JOBS_TABLE_FILENAME}.lock").chmod(0o777) # Read, Write, Execute permissions so other users can change the files
class JobsTable:
    @staticmethod
    def get_empty_table() -> pd.DataFrame:
        job_cols = [
            "id",
            "user",
            "command",
            "priority",
            "gpu_mem",
            "state",
            "timestamp",
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
            df["timestamp"] = df.timestamp.apply(pd.Timestamp)  # Oldest timestamp first

            # Sort by priority and Timestamp
            df.sort_values(by=["s", "p", "timestamp"], inplace=True)
            df.drop(["s", "p"], axis=1, inplace=True)  # Drop state and priority helper

            return df
        except FileNotFoundError:
            return JobsTable.get_empty_table()

    @staticmethod
    @lock
    def write(df: pd.DataFrame) -> None:
        df.to_csv(JOBS_TABLE_FILENAME, sep=";", index=None)
        # Read, Write, Execute permissions so other users can change the files
        JOBS_TABLE_FILENAME.chmod(0o777)

    # ================================================================= #
    @staticmethod
    @lock
    def add(args: argparse.Namespace):
        command: str = args.command
        priority: Union[Priority, str] = args.priority
        gpu_mem: float = args.gpu_mem
        verbose: int = args.verbose

        data = dict(
            id=JobsTable.get_new_valid_id(),
            user=os.getlogin(),
            command=" ".join(command),
            priority=Priority.get_valid(priority).value,
            gpu_mem=int(gpu_mem),
            state=State.PAUSED.value,
            timestamp=datetime.datetime.now(),
        )

        GpuManager.update()
        if not any(
            gpu_mem <= single_gpu for single_gpu in GpuManager.TOTAL_single.values()
        ):
            print(
                "WARNING: 'gpu_mem' exceeds any single gpu memory. Using multiple gpus..."
            )

        new_row = pd.DataFrame(data, index=[0])

        new_row["timestamp"] = new_row.timestamp.apply(pd.Timestamp)

        print(f"Adding {get_job_repr(new_row.values, lvl=verbose)} ...")

        JobsTable.write(JobsTable.read().append(new_row))

    @staticmethod
    @lock
    def update(args: argparse.Namespace):
        id: int = args.id
        attr: str = args.attr
        new_value: str = args.new_value
        verbose: int = args.verbose

        df = JobsTable.read()

        if id not in JobsTable.get_jobs_ids():
            raise ValueError(
                f"The id={id} is not a valid job id. Expected: {JobsTable.get_jobs_ids()}"
            )

        df = JobsTable.read()
        if df[(df.id == id) & (df.user == os.getlogin())].empty:
            raise PermissionError(
                f"User {os.getlogin()} not allowed to update job. Job belongs to {df[(df.id == id)].user} "
            )

        if attr == "priority":
            new_value = Priority.get_valid(new_value).value
        elif attr == "command":
            new_value = new_value
        elif attr == "gpu_mem":
            new_value = float(new_value)
        else:
            print(f"Job has no attribute/can't update attribute={attr}")
            return

        print(
            f"Updating {get_job_repr(df.loc[df.id == id].values, lvl=verbose)} . {attr}={df.loc[df.id == id][attr].values[0]} -> {attr}={new_value} ..."
        )

        df.loc[df.id == id, attr] = new_value

        JobsTable.write(df)

    @staticmethod
    @lock
    def pause(args: argparse.Namespace):
        op: str = args.op
        verbose: int = args.verbose
        if op not in ["ids", "priority", "all"]:
            raise ValueError(
                f"Expected args.op in ['ids', 'priority', 'all'] . Got: {op}"
            )

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

    @staticmethod
    @lock
    def unpause(args: argparse.Namespace):
        op: str = args.op
        verbose: int = args.verbose
        if op not in ["ids", "priority", "all"]:
            raise ValueError(
                f"Expected args.op in ['ids', 'priority', 'all'] . Got: {op}"
            )
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

    @staticmethod
    @lock
    def remove(args: argparse.Namespace):
        ids: List[int] = args.ids
        verbose: int = args.verbose

        df = JobsTable.read()

        new_df = df[(~df.id.isin(ids)) & (df.user == os.getlogin())]

        print(f"Removing {df.shape[0] - new_df.shape[0]} jobs ...")

        JobsTable.write(new_df)

    @staticmethod
    def show(args: argparse.Namespace):
        verbose: int = args.verbose
        df = JobsTable.read()

        if "id" in args and args.id is not None:
            if args.id in JobsTable.get_jobs_ids():
                print(get_job_repr(df.loc[df.id == args.id].values, lvl=verbose))
                return

            print(
                f"Job with id={args.id} does not exist. Expected: {JobsTable.get_jobs_ids()}"
            )
            return

        elif "state" in args and args.state is not None:
            jobs = df[df.state == State.get_valid(args.state).value]
            str_ = "Jobs:\n"
            for job in jobs.iterrows():
                str_ += f"  {get_job_repr([job[1].values], lvl=verbose)}\n"
            print(str_)
            return
        else:
            str_ = "Jobs:\n"
            for job in df.iterrows():
                str_ += f"  {get_job_repr([job[1].values], lvl=verbose)}\n"
            print(str_)
            return

    @staticmethod
    @lock
    def clear(args: argparse.Namespace):
        yes: bool = args.yes

        if not yes:
            raise ValueError(
                "Aborting clear command ! If you are sure you want to clear all jobs run the same command with the flag -y or --yes"
            )

        print("Clearing all jobs...")

        JobsTable.write(JobsTable.get_empty_table())

    @staticmethod
    @lock
    def clear_state(args: argparse.Namespace):
        state: str = args.state

        df = JobsTable.read()

        print(
            f"Clearing {df[df.state == State.get_valid(state).value ].shape[0]} jobs ..."
        )

        df_wo_state = df[df.state != State.get_valid(state).value]

        JobsTable.write(df_wo_state)

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
