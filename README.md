# Job queues

Add and remove jobs to a queue that can be shared by multiple users to run
scripts with different priority levels. Uses subprocess.run to run the commands.

- [Job queues](#job-queues)
  - [Requirements](#requirements)
  - [Environment](#environment)
  - [Run the server](#run-the-server)
  - [Run the client](#run-the-client)
    - [1. Show jobs](#1-show-jobs)
    - [2. Show jobs with state](#2-show-jobs-with-state)
    - [3. Add job](#3-add-job)
    - [4. Update job](#4-update-job)
    - [5. Remove job](#5-remove-job)
    - [6. Pause job](#6-pause-job)
    - [7. Unpause/Resume job](#7-unpauseresume-job)
    - [8. Clear jobs](#8-clear-jobs)
    - [9. Clear state jobs](#9-clear-state-jobs)
    - [Example usage](#example-usage)
      - [Client](#client)
      - [Server](#server)
  - [TODO](#todo)

## Requirements

- pandas
- easydict
- gpustat
- filelock

## Environment

```bash
# Create env
env_name=jobsqueue
conda create -n $env_name python=3.7 -y
conda activate $env_name

# Install package
pip install git+https://github.com/AndreGraca98/SharedJobsQueue.git

source ~/.profile


```

## Run the server

[JobsServer](/jobs_queue/server.py#L126)

```bash
JobsServer [TIME_IN_SECONDS] --threads [THREADS_NUMBER]
```

```text
usage: Server Jobs Queue [-h] [--threads THREADS] [time]

Run jobs from the jobs queue

positional arguments:
  time               Idle time (s). NOTE: It is recommended to use at least 60
                     seconds of interval time when using this tool to train
                     diferent experiments using gpus so they have enough time
                     to load the model and data instead of throwing an error.

optional arguments:
  -h, --help         show this help message and exit
  --threads THREADS  Number of jobs allowed to run at the same time
```

## Run the client

[JobsClient](/jobs_queue/client.py#L14)

```bash
JobsClient [SUBCOMMANDS]
```

```text
usage: Client Jobs Queue [-h] [-v [VERBOSE]]
                         {show,show-state,add,remove,update,pause,unpause,clear,clear-state}
                         ...

Add/Update/Remove jobs to/from the jobs queue. If no options provided show
current jobs on queue.

positional arguments:
  {show,show-state,add,remove,update,pause,unpause,clear,clear-state}
    show                Show a task in the queue
    show-state          Show tasks with state in the queue
    add                 Add a task to the queue
    remove              Remove a task from the queue
    update              Updates a task from the queue
    pause               Pause tasks from the queue
    unpause             Unpause tasks from the queue
    clear               Clears all tasks from the queue
    clear-state         Clears all state tasks from the queue

optional arguments:
  -h, --help            show this help message and exit
  -v [VERBOSE], -V [VERBOSE], --verbose [VERBOSE]
                        Verbose
```

### 1. Show jobs

[JobsClient show [...]](/jobs_queue/jobs_table.py#L210)

```bash
JobsClient
JobsClient show
JobsClient show [ID]
```

```text
usage: Client Jobs Queue show [-h] [-v [VERBOSE]] [id]

positional arguments:
  id                    Show job with specified id

optional arguments:
  -h, --help            show this help message and exit
  -v [VERBOSE], -V [VERBOSE], --verbose [VERBOSE]
                        Verbose
```

### 2. Show jobs with state

[JobsClient show-state [...]](/jobs_queue/jobs_table.py#L210)

```bash
JobsClient
JobsClient show-state [STATE]
```

```text
usage: Client Jobs Queue show-state [-h] [-v [VERBOSE]] [state]

positional arguments:
  state                 Show jobs with specified state

optional arguments:
  -h, --help            show this help message and exit
  -v [VERBOSE], -V [VERBOSE], --verbose [VERBOSE]
                        Verbose
```

### 3. Add job

[JobsClient add [...]](/jobs_queue/jobs_table.py#L79)

```bash
JobsClient add [COMMAND] -p [PRIORITY] --mem [GPU_MEM]
```

```text
usage: Client Jobs Queue add [-h] [-p PRIORITY] [--mem GPU_MEM] [-v [VERBOSE]]
                             command [command ...]

positional arguments:
  command               Command to run

optional arguments:
  -h, --help            show this help message and exit
  -p PRIORITY, -P PRIORITY, --priority PRIORITY
                        Command priority. low (1), medium/normal (2), high (3)
                        or urgent (4)
  --mem GPU_MEM, --gpu_mem GPU_MEM, --needed GPU_MEM, --needed_mem GPU_MEM, --needed_gpu_mem GPU_MEM
                        GPU memory in MB. If cmd does not require the usage of
                        graphical memory set --gpu_mem to 0.
  -v [VERBOSE], -V [VERBOSE], --verbose [VERBOSE]
                        Verbose
```

### 4. Update job

[JobsClient update [...]](/jobs_queue/jobs_table#L113)

```bash
python job_queue_client.py update [ID] [ATTR] [NEW_VALUE]
```

```text
usage: Client Jobs Queue update [-h] [-v [VERBOSE]]
                                id {priority,command,gpu_mem} new_value

positional arguments:
  id                    Job id to update from the queue
  {priority,command,gpu_mem}
  attr                      Job attribute to change
  new_value             Job attribute new value

optional arguments:
  -h, --help            show this help message and exit
  -v [VERBOSE], -V [VERBOSE], --verbose [VERBOSE]
                        Verbose
```

### 5. Remove job

[JobsClient remove [...]](/jobs_queue/jobs_table#L197)

```bash
JobsClient remove [ID_0 ... ID_n]
```

```text
usage: Client Jobs Queue remove [-h] [-v [VERBOSE]] ids [ids ...]

positional arguments:
  ids                   Job ids to remove from the queue

optional arguments:
  -h, --help            show this help message and exit
  -v [VERBOSE], -V [VERBOSE], --verbose [VERBOSE]
                        Verbose
```

### 6. Pause job

[JobsClient pause [...]](/jobs_queue/jobs_table#L152)

```bash
JobsClient pause all
JobsClient pause ids [ID_0 ... ID_n]
JobsClient pause priority [priority]
```

```text
usage: Client Jobs Queue pause [-h] [-v [VERBOSE]] {ids,priority,all} ...

optional arguments:
  -h, --help            show this help message and exit
  -v [VERBOSE], -V [VERBOSE], --verbose [VERBOSE]
                        Verbose

subcommands:
  Pause jobs with ids, priority or all waiting jobs

  {ids,priority,all}
```

### 7. Unpause/Resume job

[JobsClient unpause [...]](/jobs_queue/jobs_table#L175)

```bash
JobsClient unpause all
JobsClient unpause ids [ID_0 ... ID_n]
JobsClient unpause priority [priority]
```

```text
usage: Client Jobs Queue unpause [-h] [-v [VERBOSE]] {ids,priority,all} ...

optional arguments:
  -h, --help            show this help message and exit
  -v [VERBOSE], -V [VERBOSE], --verbose [VERBOSE]
                        Verbose

subcommands:
  Unpause jobs with ids, priority or all waiting jobs

  {ids,priority,all}
```

### 8. Clear jobs

[JobsClient clear [...]](/jobs_queue/jobs_table#L240)

```bash
JobsClient clear
JobsClient clear -y
```

```text
usage: Client Jobs Queue clear [-h] [-y]

optional arguments:
  -h, --help  show this help message and exit
  -y, --yes   Clear Job Queue
```

### 9. Clear state jobs

[JobsClient clear-state [...]](/jobs_queue/jobs_table#L254)

```bash
JobsClient clear-state [STATE]
```

```text
usage: Client Jobs Queue clear-state [-h] state

positional arguments:
  state       Clear Job State

optional arguments:
  -h, --help  show this help message and exit
```

### Example usage

#### Client

```bash
# Add bash command
$ JobsClient add /bin/bash /home/brisa/SharedJobsQueue/examples/bash_example.sh
Adding Job(id=0, command="/bin/bash /home/brisa/SharedJo[...]", priority=MEDIUM, gpu_mem=0, state=PAUSED, timestamp=12/05-14:51) ...

# Add python command
$ JobsClient add /home/brisa/anaconda3/envs/jobsqueue/bin/python /home/brisa/SharedJobsQueue/examples/sucess_example.py
Adding Job(id=1, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=0, state=PAUSED, timestamp=12/05-14:51) ...

# Add python command
$ JobsClient add /home/brisa/anaconda3/envs/jobsqueue/bin/python /home/brisa/SharedJobsQueue/examples/sleep_nsecs.py
Adding Job(id=2, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=0, state=PAUSED, timestamp=12/05-14:51) ...

# Add error example command
$ JobsClient add /home/brisa/anaconda3/envs/jobsqueue/bin/python /home/brisa/SharedJobsQueue/examples/error_example.py
Adding Job(id=3, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=0, state=PAUSED, timestamp=12/05-14:51) ...

# Add command that requires gpu usage
$ JobsClient add /home/brisa/anaconda3/envs/jobsqueue/bin/python /home/brisa/SharedJobsQueue/examples/sucess_example.py --mem 1e3
Adding Job(id=4, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=1000, state=PAUSED, timestamp=12/05-14:51) ...

# Add command that requires gpu usage with dataparallel
$ JobsClient add /home/brisa/anaconda3/envs/jobsqueue/bin/python /home/brisa/SharedJobsQueue/examples/sucess_example.py --mem 1e9
WARNING: 'gpu_mem' exceeds any single gpu memory. Using multiple gpus...
Adding Job(id=5, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=1000000000, state=PAUSED, timestamp=12/05-14:51) ...

# Add python command with urgent and high priority
$ JobsClient add /home/brisa/anaconda3/envs/jobsqueue/bin/python /home/brisa/SharedJobsQueue/examples/sucess_example.py -p 4
Adding Job(id=6, command="/home/brisa/anaconda3/envs/job[...]", priority=URGENT, gpu_mem=0, state=PAUSED, timestamp=12/05-14:51) ...
$ JobsClient add /home/brisa/anaconda3/envs/jobsqueue/bin/python /home/brisa/SharedJobsQueue/examples/sucess_example.py -p high
Adding Job(id=7, command="/home/brisa/anaconda3/envs/job[...]", priority=HIGH, gpu_mem=0, state=PAUSED, timestamp=12/05-14:51) ...

# Add python command with low priority
$ JobsClient add /home/brisa/anaconda3/envs/jobsqueue/bin/python /home/brisa/SharedJobsQueue/examples/sucess_example.py -p 1
Adding Job(id=8, command="/home/brisa/anaconda3/envs/job[...]", priority=LOW, gpu_mem=0, state=PAUSED, timestamp=12/05-14:51) ...
$ JobsClient add /home/brisa/anaconda3/envs/jobsqueue/bin/python /home/brisa/SharedJobsQueue/examples/sucess_example.py -p low
Adding Job(id=9, command="/home/brisa/anaconda3/envs/job[...]", priority=LOW, gpu_mem=0, state=PAUSED, timestamp=12/05-14:51) ...

# Show current job queue
$ JobsClient
Jobs:
  Job(id=6, command="/home/brisa/anaconda3/envs/job[...]", priority=URGENT, gpu_mem=0, state=PAUSED, timestamp=12/05-14:51)
  Job(id=7, command="/home/brisa/anaconda3/envs/job[...]", priority=HIGH, gpu_mem=0, state=PAUSED, timestamp=12/05-14:51)
  Job(id=0, command="/bin/bash /home/brisa/SharedJo[...]", priority=MEDIUM, gpu_mem=0, state=PAUSED, timestamp=12/05-14:51)
  Job(id=1, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=0, state=PAUSED, timestamp=12/05-14:51)
  Job(id=2, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=0, state=PAUSED, timestamp=12/05-14:51)
  Job(id=3, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=0, state=PAUSED, timestamp=12/05-14:51)
  Job(id=4, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=1000, state=PAUSED, timestamp=12/05-14:51)
  Job(id=5, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=1000000000, state=PAUSED, timestamp=12/05-14:51)
  Job(id=8, command="/home/brisa/anaconda3/envs/job[...]", priority=LOW, gpu_mem=0, state=PAUSED, timestamp=12/05-14:51)
  Job(id=9, command="/home/brisa/anaconda3/envs/job[...]", priority=LOW, gpu_mem=0, state=PAUSED, timestamp=12/05-14:51)


# Show waiting jobs
$ JobsClient show-state waiting
Jobs:


# Resume jobs with ids 0, 1 and 2
$ JobsClient unpause ids 0 1 2

# Show waiting jobs
$ JobsClient show-state waiting
Jobs:
  Job(id=0, command="/bin/bash /home/brisa/SharedJo[...]", priority=MEDIUM, gpu_mem=0, state=WAITING, timestamp=12/05-14:51)
  Job(id=1, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=0, state=WAITING, timestamp=12/05-14:51)
  Job(id=2, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=0, state=WAITING, timestamp=12/05-14:51)


# Remove job with id=1 and id=4 from queue
$ JobsClient remove 1 4
Removing 2 jobs ...

# Update job(id=5) priority to urgent
$ JobsClient update 5 priority 4
Updating Job(id=5, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=1000000000, state=PAUSED, timestamp=12/05-14:51) . priority=2 -> priority=4 ...

# Update job(id=5) priority to normal
$ JobsClient update 5 priority normal
Updating Job(id=5, command="/home/brisa/anaconda3/envs/job[...]", priority=URGENT, gpu_mem=1000000000, state=PAUSED, timestamp=12/05-14:51) . priority=4 -> priority=2 ...

# Remove jobs that errored
$ JobsClient clear-state error
Clearing 0 jobs ...

# Remove all jobs
$ JobsClient clear
Traceback (most recent call last):
  File "/home/brisa/bin/JobsClient", line 6, in <module>
    main_client()
  File "/home/brisa/bin/jobs_queue/client.py", line 19, in main_client
    args.operation(args)
  File "/home/brisa/anaconda3/envs/jobsqueue/lib/python3.7/contextlib.py", line 74, in inner
    return func(*args, **kwds)
  File "/home/brisa/bin/jobs_queue/jobs_table.py", line 245, in clear
    "Aborting clear command ! If you are sure you want to clear all jobs run the same command with the flag -y or --yes"
ValueError: Aborting clear command ! If you are sure you want to clear all jobs run the same command with the flag -y or --yes

# Remove all jobs
$ JobsClient clear -y
Clearing all jobs...

# Show current job queue
$ JobsClient
Jobs:

```

#### Server

```bash
# Start running jobs with idle_time=60 seconds and allow for running 2 jobs at the same time
$ JobsServer --threads 2
# KeybordInterrupt (ctrl+C)
Shutting down server...
```

## TODO

  1. [x] Make install easier.
  1. [x] Update readme.md
  1. [x] Update examples
  1. [x] In version 2.0 make it so various users can use the queue.
  1. [x] Add pause option for the tasks
  1. [ ] Add tests
  1. [ ] Better logging
