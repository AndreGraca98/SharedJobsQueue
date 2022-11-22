# Job queues

Add and remove jobs to a queue that can be shared by multiple users to run
scripts with different priority levels. Uses subprocess.run to run the commands.

- [Job queues](#job-queues)
  - [Environment](#environment)
  - [Run on the server side](#run-on-the-server-side)
  - [Run on the user side](#run-on-the-user-side)
    - [1. View job queue](#1-view-job-queue)
    - [2. Add job to queue](#2-add-job-to-queue)
    - [3. Update job from queue](#3-update-job-from-queue)
    - [4. Remove job from queue](#4-remove-job-from-queue)
    - [Example usage](#example-usage)
  - [TODO](#todo)

## Environment

```bash
folder_name=SharedJobsQueue
cd && git clone https://github.com/AndreGraca98/SharedJobsQueue.git $folder_name && cd $folder_name

env_name=jobqueue
conda create -n $env_name python=3.7 -y
conda activate $env_name
conda install -c anaconda pandas -y
pip install easydict gpustat filelock

# Use an alias to call the server or client code from 
# anywhere instead of using <python job_queue_client.py> and <python job_queue_server.py>
if alias JobQueueClient >/dev/null 2>&1; then 
  echo "alias JobQueueClient already exists in ~/.bashrc"
else
  echo "alias JobQueueClient='$HOME/anaconda3/envs/$env_name/bin/python $HOME/$folder_name/jobs_queue/client.py'" >> ~/.bashrc
fi
if alias JobQueueServer >/dev/null 2>&1; then 
  echo "alias JobQueueServer already exists in ~/.bashrc"
else
  echo "alias JobQueueServer='$HOME/anaconda3/envs/$env_name/bin/python $HOME/$folder_name/jobs_queue/server.py'" >> ~/.bashrc
fi


source ~/.bashrc

```

## Run on the server side

[JobQueueServer](/job_queue_server.py#L11)

```bash
python job_queue_server.py [TIME_IN_SECONDS]
```

```text
usage: Server Jobs Queue [-h] [--threads THREADS] [time]

Run jobs from the jobs queue

positional arguments:
  time               Idle time (s)

optional arguments:
  -h, --help         show this help message and exit
  --threads THREADS  Number of jobs allowed to run at the same time
```

## Run on the user side

[JobQueueClient](/job_queue_client.py#L20)

### 1. View job queue

[JobQueueClient -vvv](/shared_jobs_queue/queues.py#L100)

```bash
python job_queue_client.py
```

```text
usage: Client Jobs Queue [-h] [-v [VERBOSE]] {add,remove,update} ...

Add/Remove jobs to/from the jobs queue. If no options provided show current
jobs on queue.

positional arguments:
  {add,remove,update}
    add                 Add a task to the queue
    remove              Remove a task from the queue
    update              Updates a task from the queue

optional arguments:
  -h, --help            show this help message and exit
  -v [VERBOSE], -V [VERBOSE], --verbose [VERBOSE]
                        Verbose
```

### 2. Add job to queue

[JobQueueClient add ...](/shared_jobs_queue/queues.py#L24)

```bash
python job_queue_client.py add [COMMAND] -p [PRIORITY]
```

```text
usage: Client Jobs Queue add [-h] [-p PRIORITY] [-v [VERBOSE]]
                             command [command ...]

positional arguments:
  command               Command to run

optional arguments:
  -h, --help            show this help message and exit
  -p PRIORITY, -P PRIORITY, --priority PRIORITY
                        Command priority. low (1), medium/normal (2), high (3)
                        or urgent (4)
  -v [VERBOSE], -V [VERBOSE], --verbose [VERBOSE]
                        Verbose
```

### 3. Update job from queue

[JobQueueClient update ...](/shared_jobs_queue/queues.py#L37)

```bash
python job_queue_client.py update [ID] [ATTR] [NEW_VALUE]
```

```text
usage: Client Jobs Queue update [-h] [-v [VERBOSE]] id attr new_value

positional arguments:
  id                    Job id to update from the queue
  attr                  Job attribute to change
  new_value             Job attribute new value

optional arguments:
  -h, --help            show this help message and exit
  -v [VERBOSE], -V [VERBOSE], --verbose [VERBOSE]
                        Verbose
```

### 4. Remove job from queue

[JobQueueClient remove ...](/shared_jobs_queue/queues.py#L66)

```bash
python job_queue_client.py remove [ID_0 ... ID_n]
```

```text
usage: Client Jobs Queue remove [-h] [-v [VERBOSE]] id [id ...]

positional arguments:
  id                    Job ids to remove from the queue. If -1 remove all
                        jobs

optional arguments:
  -h, --help            show this help message and exit
  -v [VERBOSE], -V [VERBOSE], --verbose [VERBOSE]
                        Verbose
```

### Example usage

Client Side

```bash
# Add bash command
$ JobQueueClient add /bin/bash /home/brisa/SharedJobsQueue/examples/file.sh
Adding Job(id=0, command="/bin/bash /home/brisa/SharedJo[...]", priority=MEDIUM, gpu_mem=0, state=WAITING, timestamp=11/08-00:48)

# Add python command
$ JobQueueClient add /home/brisa/anaconda3/envs/jobqueue/bin/python /home/brisa/SharedJobsQueue/examples/sucess_example.py
Adding Job(id=1, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=0, state=WAITING, timestamp=11/08-00:48)

# Add error example command
$ JobQueueClient add /home/brisa/anaconda3/envs/jobqueue/bin/python /home/brisa/SharedJobsQueue/examples/error_example.py
Adding Job(id=2, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=0, state=WAITING, timestamp=11/08-00:48)

# Add command that requires gpu usage
$ JobQueueClient add /home/brisa/anaconda3/envs/jobqueue/bin/python /home/brisa/SharedJobsQueue/examples/sucess_example.py --mem 1e3
Adding Job(id=3, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=1000.0, state=WAITING, timestamp=11/08-00:48)

# Add python command with urgent and high priority
$ JobQueueClient add /home/brisa/anaconda3/envs/jobqueue/bin/python /home/brisa/SharedJobsQueue/examples/sucess_example.py --mem 1e9 -p 4
Adding Job(id=4, command="/home/brisa/anaconda3/envs/job[...]", priority=URGENT, gpu_mem=1000000000.0, state=WAITING, timestamp=11/08-00:48)
$ JobQueueClient add /home/brisa/anaconda3/envs/jobqueue/bin/python /home/brisa/SharedJobsQueue/examples/sucess_example.py -p 3
Adding Job(id=5, command="/home/brisa/anaconda3/envs/job[...]", priority=HIGH, gpu_mem=0, state=WAITING, timestamp=11/08-00:48)

# Add python command with low priority
$ JobQueueClient add /home/brisa/anaconda3/envs/jobqueue/bin/python /home/brisa/SharedJobsQueue/examples/sucess_example.py
Traceback (most recent call last):
  File "/home/brisa/SharedJobsQueue/job_queue_client.py", line 29, in <module>
    run()
  File "/home/brisa/SharedJobsQueue/job_queue_client.py", line 22, in run
    args.operation(queue, args)
  File "/home/brisa/SharedJobsQueue/shared_jobs_queue/queues.py", line 27, in add
    priority=get_priority(args.priority),
  File "/home/brisa/SharedJobsQueue/shared_jobs_queue/queues.py", line 13, in get_priority
    ), f"Priority not available. Expected: {Priority.__members__}. Got: {priority}"
AssertionError: Priority not available. Expected: OrderedDict([('LOW', <Priority.LOW: 1>), ('MEDIUM', <Priority.MEDIUM: 2>), ('NORMAL', <Priority.MEDIUM: 2>), ('HIGH', <Priority.HIGH: 3>), ('URGENT', <Priority.URGENT: 4>)]). Got: 0
$ JobQueueClient add /home/brisa/anaconda3/envs/jobqueue/bin/python /home/brisa/SharedJobsQueue/examples/sucess_example.py -p low
Adding Job(id=6, command="/home/brisa/anaconda3/envs/job[...]", priority=LOW, gpu_mem=0, state=WAITING, timestamp=11/08-00:48)

# Show current job queue
$ JobQueueClient
Jobs:
  Job(id=4, command="/home/brisa/anaconda3/envs/job[...]", priority=URGENT, gpu_mem=1000000000.0, state=WAITING, timestamp=11/08-00:48)
  Job(id=5, command="/home/brisa/anaconda3/envs/job[...]", priority=HIGH, gpu_mem=0, state=WAITING, timestamp=11/08-00:48)
  Job(id=0, command="/bin/bash /home/brisa/SharedJo[...]", priority=MEDIUM, gpu_mem=0, state=WAITING, timestamp=11/08-00:48)
  Job(id=1, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=0, state=WAITING, timestamp=11/08-00:48)
  Job(id=2, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=0, state=WAITING, timestamp=11/08-00:48)
  Job(id=3, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=1000.0, state=WAITING, timestamp=11/08-00:48)
  Job(id=6, command="/home/brisa/anaconda3/envs/job[...]", priority=LOW, gpu_mem=0, state=WAITING, timestamp=11/08-00:48)

# Remove job with id=1 and id=4 from queue
$ JobQueueClient remove 1 4
Removing Job(id=1, command="/home/brisa/anaconda3/envs/job[...]", priority=MEDIUM, gpu_mem=0, state=WAITING, timestamp=11/08-00:48)
Removing Job(id=4, command="/home/brisa/anaconda3/envs/job[...]", priority=URGENT, gpu_mem=1000000000.0, state=WAITING, timestamp=11/08-00:48)

# Update job(id=5) priority to urgent
$ JobQueueClient update 5 priority 4
Updating Job(id=5, command="/home/brisa/anaconda3/envs/job[...]", priority=HIGH, gpu_mem=0, state=WAITING, timestamp=11/08-00:48) . priority=Priority.HIGH -> priority=Priority.URGENT

# Update job(id=5) priority to normal
$ JobQueueClient update 5 priority normal
Updating Job(id=5, command="/home/brisa/anaconda3/envs/job[...]", priority=URGENT, gpu_mem=0, state=WAITING, timestamp=11/08-00:48) . priority=Priority.URGENT -> priority=Priority.MEDIUM

# Remove all jobs
$ JobQueueClient clear 
Aborting clear command ! If you are sure you want to clear all jobs run the same command with the flag -y or --yes
$ JobQueueClient clear -y
Clearing all jobs...
```

Server Side

```bash
# Start running jobs with idle_time=60 seconds
$ JobQueueServer

2022-11-08 00:49:31.328390 :INFO: Idle ...

```

## TODO

  [ ] Make install easier.
  [ ] Update readme.md
  [x] In version 2.0 make it so various users can use the queue.
