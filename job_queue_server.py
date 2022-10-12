import datetime
import subprocess
import time
from pathlib import Path

from shared_jobs_queue.args import get_args
from shared_jobs_queue.queues import JobsQueue
from shared_jobs_queue.tools import fpkl, ftext


def run():
    args = get_args(client_args=False)
    sleep_time = args.time
    
    QUEUE_FILENAME:str = ".JOBS_QUEUE.pkl"
    QUEUE_LOG_FILENAME:str = ".JOBS_QUEUE.log"
    path = (Path.home() / Path(QUEUE_FILENAME)).resolve()
    log_path = (Path.home() / Path(QUEUE_LOG_FILENAME)).resolve()

    idle_state = False
    while True:
        try:
            try:
                queue = fpkl.read(path)
            except FileNotFoundError:
                # If file does not exist create new empty queue
                queue = JobsQueue()
                fpkl.write(path, queue)

            job = queue.get_next_job()

            if job is None and not idle_state:
                idle_state = True
                # No jobs to run

                # Log
                log_str = f"{datetime.datetime.now()} :INFO: Idle ...\n"
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
            print("Starting job:", job)
            ftext.append(log_path, f"{datetime.datetime.now()} :INFO: Starting job: {job}\n")

            # Update queue
            fpkl.write(path, queue)
            
            # Run job
            command, *args = job.command.split()
            code = subprocess.run([job.env, command, *args])

            # Log
            print("Finished code:", code)
            ftext.append(
                log_path, f"{datetime.datetime.now()} : {'SUCCSSESS' if code.returncode == 0 else 'ERROR'} : {code} \n"
            )
            
        except KeyboardInterrupt:
            ftext.append(
                    log_path, f"{datetime.datetime.now()} : ERROR : KeyboardInterrupt \n"
                )
            print()
            break


if __name__ == "__main__":
    run()

# ENDFILE
