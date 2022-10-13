# Job queues

Add and remove jobs to a queue that can be shared by multiple users to run
scripts with different priority levels. Uses subprocess.run to run the commands.

- [Job queues](#job-queues)
  - [Environment](#environment)
  - [Run on the server side](#run-on-the-server-side)
  - [Run on the user side](#run-on-the-user-side)
    - [1. View job queue](#1-view-job-queue)
    - [2. Add job to queue](#2-add-job-to-queue)
    - [3. Remove job from queue](#3-remove-job-from-queue)
    - [4. Update job from queue](#4-update-job-from-queue)
    - [Example usage](#example-usage)
  - [TODO](#todo)

## Environment

```bash
folder_name=SharedJobsQueue
cd && git clone https://github.com/AndreGraca98/SharedJobsQueue.git $folder_name && cd $folder_name

env_name=jobqueue
conda create -n $env_name python=3.7 -y
conda activate $env_name

# Use an alias to call the server or client code from 
# anywhere instead of using <python job_queue_client.py> and <python job_queue_server.py>
if alias JobQueueClient >/dev/null 2>&1; then 
  echo "alias JobQueueClient already exists in ~/.bashrc"
else
  echo "alias JobQueueClient='$HOME/anaconda3/envs/$env_name/bin/python $HOME/$folder_name/job_queue_client.py'" >> ~/.bashrc
fi
if alias JobQueueServer >/dev/null 2>&1; then 
  echo "alias JobQueueServer already exists in ~/.bashrc"
else
  echo "alias JobQueueServer='$HOME/anaconda3/envs/$env_name/bin/python $HOME/$folder_name/job_queue_server.py'" >> ~/.bashrc
fi




```

## Run on the server side

[JobQueueServer](/job_queue_server.py#L11)

```bash
python job_queue_server.py [TIME_IN_SECONDS]
```

```text
usage: Server Jobs Queue [-h] [time]

Run jobs from the jobs queue

positional arguments:
  time        Idle time (s)

optional arguments:
  -h, --help  show this help message and exit
```

## Run on the user side

[JobQueueClient](/job_queue_client.py#L20)

### 1. View job queue

[JobQueueClient -vvv](/shared_jobs_queue/queues.py#L78)

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

[JobQueueClient add ...](/shared_jobs_queue/queues.py#L14)

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

### 3. Remove job from queue

[JobQueueClient remove ...](/shared_jobs_queue/queues.py#L45)

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

### 4. Update job from queue

[JobQueueClient update ...](/shared_jobs_queue/queues.py#L81)

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

### Example usage

Client Side

```bash
# Add bash command
$ JobQueueClient add /bin/bash SharedJobsQueue/examples/file.sh
Adding new job Job(_id=0, user=brisa, command="/bin/bash SharedJobsQueue/examples/file.sh", priority=Priority.MEDIUM, timestamp=2022-10-12 15:55:51.306625) ...

# Add python command
$ JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python SharedJobsQueue/random_sleep.py
Adding new job Job(_id=1, user=brisa, command="/home/brisa/anaconda3/envs/jobqueue/bin/python SharedJobsQueue/random_sleep.py", priority=Priority.MEDIUM, timestamp=2022-10-12 15:55:51.367649) ...
$ JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python SharedJobsQueue/random_sleep.py
Adding new job Job(_id=2, user=brisa, command="/home/brisa/anaconda3/envs/jobqueue/bin/python SharedJobsQueue/random_sleep.py", priority=Priority.MEDIUM, timestamp=2022-10-12 15:55:51.427472) ...
$ JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python SharedJobsQueue/random_sleep.py
Adding new job Job(_id=3, user=brisa, command="/home/brisa/anaconda3/envs/jobqueue/bin/python SharedJobsQueue/random_sleep.py", priority=Priority.MEDIUM, timestamp=2022-10-12 15:55:51.483814) ...

# Add python command with high priority
$ JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python SharedJobsQueue/random_sleep.py -p 3
Adding new job Job(_id=4, user=brisa, command="/home/brisa/anaconda3/envs/jobqueue/bin/python SharedJobsQueue/random_sleep.py", priority=Priority.HIGH, timestamp=2022-10-12 15:55:51.539693) ...

# Add python command with low priority
$ JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python SharedJobsQueue/random_sleep.py -p low
Adding new job Job(_id=5, user=brisa, command="/home/brisa/anaconda3/envs/jobqueue/bin/python SharedJobsQueue/random_sleep.py", priority=Priority.LOW, timestamp=2022-10-12 15:55:51.596815) ...

# Show current job queue
$ JobQueueClient
Jobs:
  Job(_id=4, user=brisa, command="/home/brisa/anaconda3/envs/jobqueue/bin/python SharedJobsQueue/random_sleep.py", priority=Priority.HIGH, timestamp=2022-10-12 15:55:51.539693)
  Job(_id=0, user=brisa, command="/bin/bash SharedJobsQueue/examples/file.sh", priority=Priority.MEDIUM, timestamp=2022-10-12 15:55:51.306625)
  Job(_id=1, user=brisa, command="/home/brisa/anaconda3/envs/jobqueue/bin/python SharedJobsQueue/random_sleep.py", priority=Priority.MEDIUM, timestamp=2022-10-12 15:55:51.367649)
  Job(_id=2, user=brisa, command="/home/brisa/anaconda3/envs/jobqueue/bin/python SharedJobsQueue/random_sleep.py", priority=Priority.MEDIUM, timestamp=2022-10-12 15:55:51.427472)
  Job(_id=3, user=brisa, command="/home/brisa/anaconda3/envs/jobqueue/bin/python SharedJobsQueue/random_sleep.py", priority=Priority.MEDIUM, timestamp=2022-10-12 15:55:51.483814)
  Job(_id=5, user=brisa, command="/home/brisa/anaconda3/envs/jobqueue/bin/python SharedJobsQueue/random_sleep.py", priority=Priority.LOW, timestamp=2022-10-12 15:55:51.596815)

# Remove job with id=1 from queue
$ JobQueueClient remove 1
Removing job Job(_id=1, user=brisa, command="/home/brisa/anaconda3/envs/jobqueue/bin/python SharedJobsQueue/random_sleep.py", priority=Priority.MEDIUM, timestamp=2022-10-12 15:55:51.367649) ...

# Remove job with id=2 and id=3 from queue
$ JobQueueClient remove 2 3
Removing job Job(_id=2, user=brisa, command="/home/brisa/anaconda3/envs/jobqueue/bin/python SharedJobsQueue/random_sleep.py", priority=Priority.MEDIUM, timestamp=2022-10-12 15:55:51.427472) ...
Removing job Job(_id=3, user=brisa, command="/home/brisa/anaconda3/envs/jobqueue/bin/python SharedJobsQueue/random_sleep.py", priority=Priority.MEDIUM, timestamp=2022-10-12 15:55:51.483814) ...

# Show current job queue
$ JobQueueClient
Jobs:
  Job(_id=4, user=brisa, command="/home/brisa/anaconda3/envs/jobqueue/bin/python SharedJobsQueue/random_sleep.py", priority=Priority.HIGH, timestamp=2022-10-12 15:55:51.539693)
  Job(_id=0, user=brisa, command="/bin/bash SharedJobsQueue/examples/file.sh", priority=Priority.MEDIUM, timestamp=2022-10-12 15:55:51.306625)
  Job(_id=5, user=brisa, command="/home/brisa/anaconda3/envs/jobqueue/bin/python SharedJobsQueue/random_sleep.py", priority=Priority.LOW, timestamp=2022-10-12 15:55:51.596815)

# Update job(id=5) priority to urgent
$ JobQueueClient update 5 priority 4
Updating job(id=2, ...) . priority=Priority.LOW -> priority=Priority.URGENT

# Update job(id=5) priority to normal
$ JobQueueClient update 5 priority normal
Updating job(id=2, ...) . priority=Priority.URGENT -> priority=Priority.MEDIUM

# Remove all jobs
$ JobQueueClient remove -1
Removing all jobs ids=[0, 4, 5]...

```

Server Side

```bash
# Start running jobs with idle_time=1 second
$ JobQueueServer 1
2022-10-12 16:12:44.597015 :INFO: Idle ...

```

## TODO

  [ ] Make install easier
  [ ] In version 2.0 make it so various users can use the queue
