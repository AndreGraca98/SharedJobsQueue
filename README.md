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
cd && git clone https://github.com/AndreGraca98/SharedJobsQueue.git SharedJobsQueue_2

env_name=jobqueue
conda create -n $env_name python=3.7 -y
conda activate $env_name

# Use an alias to call the server or client code from anywhere
alias JobQueueClient='$HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue_2/job_queue_client.py'
alias JobQueueServer='$HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue_2/job_queue_server.py'
```

## Run on the server side

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

### View job queue

```bash
python job_queue_client.py
```

```text
usage: Client Jobs Queue [-h] {add,remove} ...

Add/Remove jobs to/from the jobs queue. If no options provided show current
jobs on queue.

positional arguments:
  {add,remove}
    add         Add a task to the queue
    remove      Remove a task from the queue

optional arguments:
  -h, --help    show this help message and exit
```

### Add job to queue

```bash
python job_queue_client.py add [ENV] [COMMAND] -p [PRIORITY]
```

```text
usage: Client Jobs Queue add [-h] [-p PRIORITY] env command [command ...]

positional arguments:
  env                   Environment to run the command
  command               Command to run

optional arguments:
  -h, --help            show this help message and exit
  -p PRIORITY, -P PRIORITY, --priority PRIORITY
                        Command priority. low (1), medium/normal (2), high (3)
                        or urgent (4)
```

### Remove job from queue

```bash
python job_queue_client.py remove [ID]
```

```text
usage: Client Jobs Queue remove [-h] id

positional arguments:
  id          Job id to remove from the queue

optional arguments:
  -h, --help  show this help message and exit
```

### Example usage

Client Side

```bash
# Add bash command
$ python job_queue_client.py add /bin/bash bash_file.sh
Adding new job Job(_id=0, user=brisa, env="/bin/bash", command="examples/bash_file.sh", priority=Priority.MEDIUM, timestamp=2022-10-11 22:31:47.430254) ...

# Add python command
$ python job_queue_client.py add $HOME/anaconda3/envs/$env_name/bin/python examples/random_sleep.py
Adding new job Job(_id=1, user=brisa, env="/home/brisa/anaconda3/envs/jobqueue/bin/python", command="examples/random_sleep.py", priority=Priority.MEDIUM, timestamp=2022-10-11 22:32:18.120021) ...

# Add python command with urgent priority
$ python job_queue_client.py add $HOME/anaconda3/envs/$env_name/bin/python examples/random_sleep.py  -p 4
Adding new job Job(_id=2, user=brisa, env="/home/brisa/anaconda3/envs/jobqueue/bin/python", command="examples/random_sleep.py", priority=Priority.URGENT, timestamp=2022-10-11 22:32:31.319041) ...

# Add python command with low priority
$ python job_queue_client.py add $HOME/anaconda3/envs/$env_name/bin/python examples/random_sleep.py  -p 1
Adding new job Job(_id=3, user=brisa, env="/home/brisa/anaconda3/envs/jobqueue/bin/python", command="examples/random_sleep.py", priority=Priority.LOW, timestamp=2022-10-11 22:33:02.852515) ...

# Show current job queue
$ python job_queue_client.py
Jobs:
  Job(_id=2, user=brisa, env="/home/brisa/anaconda3/envs/jobqueue/bin/python", command="examples/random_sleep.py", priority=Priority.URGENT, timestamp=2022-10-11 22:32:31.319041)
  Job(_id=0, user=brisa, env="/bin/bash", command="examples/bash_file.sh", priority=Priority.MEDIUM, timestamp=2022-10-11 22:31:47.430254)
  Job(_id=1, user=brisa, env="/home/brisa/anaconda3/envs/jobqueue/bin/python", command="examples/random_sleep.py", priority=Priority.MEDIUM, timestamp=2022-10-11 22:32:18.120021)
  Job(_id=3, user=brisa, env="/home/brisa/anaconda3/envs/jobqueue/bin/python", command="examples/random_sleep.py", priority=Priority.LOW, timestamp=2022-10-11 22:33:02.852515)

# Remove job with id=1 from queue
$ python job_queue_client.py remove 1
Removing job Job(_id=1, user=brisa, env="/home/brisa/anaconda3/envs/jobqueue/bin/python", command="examples/random_sleep.py", priority=Priority.MEDIUM, timestamp=2022-10-11 22:32:18.120021) ...

# Show current job queue
$ python job_queue_client.py
Jobs:
  Job(_id=2, user=brisa, env="/home/brisa/anaconda3/envs/jobqueue/bin/python", command="examples/random_sleep.py", priority=Priority.URGENT, timestamp=2022-10-11 22:32:31.319041)
  Job(_id=0, user=brisa, env="/bin/bash", command="examples/bash_file.sh", priority=Priority.MEDIUM, timestamp=2022-10-11 22:31:47.430254)
  Job(_id=3, user=brisa, env="/home/brisa/anaconda3/envs/jobqueue/bin/python", command="examples/random_sleep.py", priority=Priority.LOW, timestamp=2022-10-11 22:33:02.852515)

```

Server Side

```bash
# Start running jobs with idle_time=1 second
$ python job_queue_server.py 1
Starting job: Job(_id=2, user=brisa, env="/home/brisa/anaconda3/envs/jobqueue/bin/python", command="examples/random_sleep.py", priority=Priority.URGENT, timestamp=2022-10-11 22:32:31.319041)
Sleeping 4.00s
Finished code: CompletedProcess(args=['/home/brisa/anaconda3/envs/jobqueue/bin/python', 'examples/random_sleep.py'], returncode=0)
Starting job: Job(_id=0, user=brisa, env="/bin/bash", command="examples/bash_file.sh", priority=Priority.MEDIUM, timestamp=2022-10-11 22:31:47.430254)
Sleeping 4.45s
finished running the bash script!
Finished code: CompletedProcess(args=['/bin/bash', 'examples/bash_file.sh'], returncode=0)
Starting job: Job(_id=3, user=brisa, env="/home/brisa/anaconda3/envs/jobqueue/bin/python", command="examples/random_sleep.py", priority=Priority.LOW, timestamp=2022-10-11 22:33:02.852515)
Sleeping 4.50s
Finished code: CompletedProcess(args=['/home/brisa/anaconda3/envs/jobqueue/bin/python', 'examples/random_sleep.py'], returncode=0)
2022-10-11 22:35:58.234393 :INFO: Idle ...

```
