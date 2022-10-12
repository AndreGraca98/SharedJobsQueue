if [ $# -eq 0 ]; then
    env_name=jobqueue
else
    env_name=$1
fi


JobQueueClient(){
    python $HOME/SharedJobsQueue/job_queue_client.py "$@"
}


JobQueueClient add /bin/bash SharedJobsQueue/examples/file.sh

JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python SharedJobsQueue/examples/random_sleep.py
JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python SharedJobsQueue/examples/random_sleep.py
JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python SharedJobsQueue/examples/random_sleep.py

JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python SharedJobsQueue/examples/random_sleep.py -p 3

JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python SharedJobsQueue/examples/random_sleep.py -p low

JobQueueClient

JobQueueClient remove 1
JobQueueClient remove 2 3

JobQueueClient

JobQueueClient update 5 priority 4
JobQueueClient update 5 priority normal

JobQueueClient remove -1
