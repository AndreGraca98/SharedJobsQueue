from pathlib import Path

from shared_jobs_queue.args import get_args
from shared_jobs_queue.queues import JobsQueue
from shared_jobs_queue.tools import fpkl


def run():
    DIR = Path("/tmp/jobs_queue/")
    DIR.mkdir(parents=True, exist_ok=True)

    path = DIR / ".JOBS_QUEUE.pkl"

    try:
        queue = fpkl.read(Path(path).resolve())
    except FileNotFoundError:
        # If file does not exist create new empty queue
        queue = JobsQueue()

    args = get_args(client_args=True)
    args.operation(queue, args)

    # Update Queue
    fpkl.write(path, queue)


if __name__ == "__main__":
    run()


# ENDFILE
