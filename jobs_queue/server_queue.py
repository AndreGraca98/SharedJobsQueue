#!/usr/bin/env python


import datetime
import os
import pwd
import subprocess
import time
from enum import Enum
from multiprocessing import Process
from pathlib import Path
from typing import Union

from .gpu_memory import GpuManager, GpuMemoryOutOfRange, wait_for_free_space
from .jobs import State as JobState
from .jobs import get_job_repr
from .jobs_table import JOBS_TABLE_FILENAME, JobsTable
from .server_args import get_args
from .tools import ftext

__all__ = ["main"]


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


def get_process_as_user(cmd: str, username: str, working_dir: str):
    def demote(user_uid: int, user_gid: int):
        def result():
            os.setgid(user_gid)
            os.setuid(user_uid)

        return result

    pw_record = pwd.getpwnam(username)

    env = os.environ.copy()

    env["HOME"] = pw_record.pw_dir
    env["LOGNAME"] = pw_record.pw_name
    env["PWD"] = working_dir
    env["USER"] = pw_record.pw_name

    process = subprocess.Popen(
        cmd,
        preexec_fn=demote(pw_record.pw_uid, pw_record.pw_gid),
        cwd=working_dir,
        env=env,
        shell=True,  # To use cmd as a string and catch errors in main func
    )

    return process


def run_server(sleep_time: int = 60):
    # os.umask(0000)  # so everyone can read, write and execute

    log_path = JOBS_TABLE_FILENAME.with_suffix(".log")
    # Read, Write, Execute permissions so other users can change the files
    log_path.touch(0o770)

    server_state = State.IDLE

    while True:
        try:
            time.sleep(sleep_time)
            job = JobsTable.get_next_job()

            if job is None and server_state is not State.IDLE:
                # No jobs to run
                server_state = State.IDLE

                # Log
                Log.INFO(f"Idle ...\n", log_path)

                continue

            elif job is None and server_state is State.IDLE:
                # Idle
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

            # TODO: Add other options to use the device. Also maybe customizable
            # by user in settings
            if job.gpu_mem.values[0] == 0.0:
                device = ""  # FIXME : Use 'cpu' or ''
            elif device is True:
                device = ""  # --data_parallel
            else:
                device = f"cuda:{device}"  # --device cuda:{device}

            cmd: str = job.command.values[0]
            cmd = cmd.replace("python", job.env_path.values[0])

            proc = get_process_as_user(
                f"{cmd} {device}",
                job.user.values[0],
                job.working_dir.values[0],
            )

            # Update job pid and start time
            JobsTable.update_job(job.id.values[0], "pid", int(proc.pid))
            JobsTable.update_job(job.id.values[0], "stime", datetime.datetime.now())

            # Wait for process to finish
            returncode = proc.wait()

            # Update job finished time
            JobsTable.update_job(job.id.values[0], "pid", "---")
            JobsTable.update_job(job.id.values[0], "ftime", datetime.datetime.now())

            JobsTable.set_job_state(
                job.id.values[0],
                state=JobState.DONE if returncode == 0 else JobState.ERROR,
            )

            Log["SUCCESS" if returncode == 0 else "ERROR"](
                f"On {get_job_repr(job.values, 1)}\n", log_path
            )

            time.sleep(sleep_time)

        except KeyboardInterrupt:
            if job is not None:
                # Update job finished time
                JobsTable.update_job(job.id.values[0], "pid", "---")
                JobsTable.update_job(job.id.values[0], "ftime", datetime.datetime.now())

                JobsTable.set_job_state(job.id.values[0], state=JobState.ERROR)
            print("\rShutting down server...")
            break

        except GpuMemoryOutOfRange:
            # Update job finished time
            JobsTable.update_job(job.id.values[0], "pid", "---")
            JobsTable.update_job(job.id.values[0], "ftime", datetime.datetime.now())

            JobsTable.set_job_state(job.id.values[0], state=JobState.ERROR)

            Log.ERROR(
                f"GpuMemoryOutOfRange(Requested={job.gpu_mem.values[0]} MB, Available={GpuManager.TOTAL} MB) \n",
                log_path,
            )


def main():
    args = get_args()
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


# ENDFILE
