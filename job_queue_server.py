import datetime
import subprocess
import time
from pathlib import Path

from shared_jobs_queue.args import get_args
from shared_jobs_queue.queues import JobsQueue
from shared_jobs_queue.tools import fpkl, ftext
from shared_jobs_queue.gpu_memory import (
    GpuManager,
    GpuMemoryOutOfRange,
    wait_for_free_space,
)


def run():
    args = get_args(client_args=False)
    sleep_time = args.time

    DIR = Path("/tmp/jobs_queue/")
    path = DIR / ".JOBS_QUEUE.pkl"
    log_path = DIR / ".JOBS_QUEUE.log"

    idle_state = False
    while True:
        try:
            try:
                queue = fpkl.read(path)
            except FileNotFoundError:
                # If file does not exist create new empty queue
                DIR.mkdir(parents=True, exist_ok=True)

                queue = JobsQueue()
                fpkl.write(path, queue)

            job = queue.get_next_job()

            if job is None and not idle_state:
                idle_state = True
                # No jobs to run

                # Log
                log_str = f"\n{datetime.datetime.now()} :INFO: Idle ...\n"
                print(log_str)
                ftext.append(log_path, log_str)

                time.sleep(sleep_time)
                continue

            elif job is None and idle_state:
                # Idle
                time.sleep(sleep_time)
                continue
            else:
                # New jobs found
                idle_state = False

            # Log
            print("Starting job:", job._full_str_)
            ftext.append(
                log_path,
                f"\n{datetime.datetime.now()} :INFO: Starting job: {job._full_str_}\n",
            )

            # Update queue
            fpkl.write(path, queue)

            # Run job
            wait_for_free_space(
                job.needed_gpu_mem, verbose=True
            )  # Might throw GpuMemoryOutOfRange

            code = subprocess.run(job.command, shell=True)
            job.update_state()

            fpkl.write(path, queue)

            # Log
            print("Finished code:", code)
            ftext.append(
                log_path,
                f"{datetime.datetime.now()} : {'SUCCESS' if code.returncode == 0 else 'ERROR'} : {code} \n",
            )

        except GpuMemoryOutOfRange:
            if job is not None:
                job.set_state(-1)
                fpkl.write(path, queue)

            ftext.append(
                log_path,
                f"{datetime.datetime.now()} : ERROR : GpuMemoryOutOfRange(Requested={job.needed_gpu_mem} MB, Available={GpuManager.TOTAL} MB) \n",
            )
            print(
                f"{datetime.datetime.now()} : ERROR : GpuMemoryOutOfRange(Requested={job.needed_gpu_mem} MB, Available={GpuManager.TOTAL} MB). {job} \n"
            )

        except KeyboardInterrupt:
            if job is not None:
                job.set_state(-1)
                fpkl.write(path, queue)

            ftext.append(
                log_path, f"{datetime.datetime.now()} : ERROR : KeyboardInterrupt \n"
            )
            print()
            break


if __name__ == "__main__":

    run()

# ENDFILE
