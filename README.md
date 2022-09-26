# Job queues

Add and remove jobs to a queue that can be shared by multiple users to run
scripts with different priority levels. Uses os.system to run the commands.

- [Job queues](#job-queues)
  - [Environment](#environment)
  - [Run on the server side](#run-on-the-server-side)
  - [Run on the user side](#run-on-the-user-side)
    - [View job queue](#view-job-queue)
    - [Add job to queue](#add-job-to-queue)
    - [Remove job from queue](#remove-job-from-queue)
    - [Example usage](#example-usage)

## Environment

```bash
conda create -n shared_queue python=3.7
conda activate shared_queue
```

## Run on the server side

```bash
python job_runner.py 
```

## Run on the user side

### View job queue

```bash
python job_queue.py
```

```text
usage: Jobs Queue [-h] {add,remove} ...

Add/Remove jobs to/from the jobs queue. If no options provided show current jobs on queue.

positional arguments:
  {add,remove}
    add         Add a task to the queue
    remove      Remove a task from the queue

optional arguments:
  -h, --help    show this help message and exit
```

### Add job to queue

```bash
python job_queue.py add [COMMAND] -p [PRIORITY]
```

```text
usage: Jobs Queue add [-h] [-p PRIORITY] command

positional arguments:
  command               Command to run

optional arguments:
  -h, --help            show this help message and exit
  -p PRIORITY, --priority PRIORITY
                        Command priority. low, medium/normal, high or urgent
```

### Remove job from queue

```bash
python job_queue.py remove [ID]
```

```text
usage: Jobs Queue remove [-h] id

positional arguments:
  id          Job id to remove from the queue

optional arguments:
  -h, --help  show this help message and exit
```

### Example usage

```bash
$ python job_queue.py add "python shared_jobs_queue/random_sleep.py" -p low
Adding new job Job(_id=0, user=brisa, command="python shared_jobs_queue/random_sleep.py", priority=Priority.LOW, timestamp=2022-09-26 17:35:05.308246) ...
$ python job_queue.py add "python shared_jobs_queue/random_sleep.py" -p urgent
Adding new job Job(_id=1, user=brisa, command="python shared_jobs_queue/random_sleep.py", priority=Priority.URGENT, timestamp=2022-09-26 17:35:08.842911) ...
$ python job_queue.py add "python shared_jobs_queue/random_sleep.py" -p low
Adding new job Job(_id=2, user=brisa, command="python shared_jobs_queue/random_sleep.py", priority=Priority.LOW, timestamp=2022-09-26 17:35:16.710135) ...
$ python job_queue.py add "python shared_jobs_queue/random_sleep.py" -p low
Adding new job Job(_id=3, user=brisa, command="python shared_jobs_queue/random_sleep.py", priority=Priority.LOW, timestamp=2022-09-26 17:35:18.213817) ...
$ python job_queue.py
Jobs:
  Job(_id=1, user=brisa, command="python shared_jobs_queue/random_sleep.py", priority=Priority.URGENT, timestamp=2022-09-26 17:35:08.842911)
  Job(_id=0, user=brisa, command="python shared_jobs_queue/random_sleep.py", priority=Priority.LOW, timestamp=2022-09-26 17:35:05.308246)
  Job(_id=2, user=brisa, command="python shared_jobs_queue/random_sleep.py", priority=Priority.LOW, timestamp=2022-09-26 17:35:16.710135)
  Job(_id=3, user=brisa, command="python shared_jobs_queue/random_sleep.py", priority=Priority.LOW, timestamp=2022-09-26 17:35:18.213817)
$ python job_queue.py remove 0
Removing job Job(_id=0, user=brisa, command="python shared_jobs_queue/random_sleep.py", priority=Priority.LOW, timestamp=2022-09-26 17:35:05.308246) ...
$ python job_queue.py
Jobs:
  Job(_id=1, user=brisa, command="python shared_jobs_queue/random_sleep.py", priority=Priority.URGENT, timestamp=2022-09-26 17:35:08.842911)
  Job(_id=2, user=brisa, command="python shared_jobs_queue/random_sleep.py", priority=Priority.LOW, timestamp=2022-09-26 17:35:16.710135)
  Job(_id=3, user=brisa, command="python shared_jobs_queue/random_sleep.py", priority=Priority.LOW, timestamp=2022-09-26 17:35:18.213817)
```
