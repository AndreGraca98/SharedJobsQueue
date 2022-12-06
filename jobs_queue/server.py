#!/usr/bin/env python


import datetime
import subprocess
import time
from enum import Enum
from multiprocessing import Process
from pathlib import Path
from typing import Union

try:
    from args import get_args
    from gpu_memory import GpuManager, GpuMemoryOutOfRange, wait_for_free_space
    from jobs import State as JobState
    from jobs import get_job_repr
    from jobs_table import JOBS_TABLE_FILENAME, JobsTable
    from tools import ftext
except ModuleNotFoundError:
    from .args import get_args
    from .gpu_memory import GpuManager, GpuMemoryOutOfRange, wait_for_free_space
    from .jobs import State as JobState
    from .jobs import get_job_repr
    from .jobs_table import JOBS_TABLE_FILENAME, JobsTable
    from .tools import ftext

__all__ = ["main_server"]


class State:
    "Server State"
    IDLE = 0
    PROCESSING = 1
    FULL = 2


class Log(Enum):
    INFO = "INFO"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"

    def __call__(self, log_str: str, path: Union[Path, str]):
        str_ = f"\n{datetime.datetime.now()}: {self.value} : {log_str}"

        ftext.append(path, str_)
        print(str_)


def run_server(sleep_time: int = 60):

    log_path = JOBS_TABLE_FILENAME.with_suffix(".log")
    # Read, Write, Execute permissions so other users can change the files
    log_path.touch(0o777)

    server_state = State.IDLE

    while True:
        try:
            job = JobsTable.get_next_job()

            if job is None and server_state is not State.IDLE:
                # No jobs to run
                server_state = State.IDLE

                # Log
                Log.INFO(f"Idle ...\n", log_path)

                time.sleep(sleep_time)
                continue

            elif job is None and server_state is State.IDLE:
                # Idle
                time.sleep(sleep_time)
                continue

            else:
                # New jobs found
                server_state = State.PROCESSING

            device = wait_for_free_space(
                job.gpu_mem.values[0], sleep_time_secs=sleep_time
            )

            Log.INFO(
                f"Starting job: {get_job_repr(job.values, lvl=-1)}\n",
                log_path,
            )

            if job.gpu_mem.values[0] == 0.0:
                device = ""  # FIXME : Use 'cpu' or ''
            elif device is True:
                device = ""  # --data_parallel
            else:
                device = f"cuda:{device}"  # --device cuda:{device}

            code = subprocess.run(
                f"{job.command.values[0]} {device}",
                shell=True,
                stderr=open(log_path, "a+"),
            )

            JobsTable.set_job_state(
                job.id.values[0],
                state=JobState.DONE if code.returncode == 0 else JobState.ERROR,
            )

            Log["SUCCESS" if code.returncode == 0 else "ERROR"](
                f"On {get_job_repr(job.values, 1)} -> {code}\n", log_path
            )

            time.sleep(sleep_time)

        except KeyboardInterrupt:
            if job is not None:
                JobsTable.set_job_state(job.id.values[0], state=JobState.ERROR)
            print("\rShutting down server...")
            break
        except GpuMemoryOutOfRange:
            JobsTable.set_job_state(job.id.values[0], state=JobState.ERROR)

            Log.ERROR(
                f"GpuMemoryOutOfRange(Requested={job.gpu_mem.values[0]} MB, Available={GpuManager.TOTAL} MB) \n",
                log_path,
            )


def main_server():
    args = get_args(client=False)
    sleep_time = args.time
    nthreads = args.threads

    threads = [Process(target=run_server, args=(sleep_time,)) for _ in range(nthreads)]

    try:
        for thread in threads:
            thread.start()
            time.sleep(sleep_time)

        for thread in threads:
            thread.join()
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main_server()


# ENDFILE
