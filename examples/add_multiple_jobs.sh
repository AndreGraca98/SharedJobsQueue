if [ $# -eq 0 ]; then
    env_name=jobqueue
else
    env_name=$1
fi



python job_queue_client.py add "$HOME/anaconda3/envs/$env_name/bin/python" "$HOME/SharedJobsQueue/examples/random_sleep.py" -p high
python job_queue_client.py add "$HOME/anaconda3/envs/$env_name/bin/python" "$HOME/SharedJobsQueue/examples/random_sleep.py"
python job_queue_client.py add "$HOME/anaconda3/envs/$env_name/bin/python" "$HOME/SharedJobsQueue/examples/random_sleep.py" -p urgent
python job_queue_client.py add "$HOME/anaconda3/envs/$env_name/bin/python" "$HOME/SharedJobsQueue/examples/random_sleep.py"
python job_queue_client.py add "$HOME/anaconda3/envs/$env_name/bin/python" "$HOME/SharedJobsQueue/examples/random_sleep.py" -p urgent
python job_queue_client.py add "$HOME/anaconda3/envs/$env_name/bin/python" "$HOME/SharedJobsQueue/examples/random_sleep.py" -p low
python job_queue_client.py add "$HOME/anaconda3/envs/$env_name/bin/python" "$HOME/SharedJobsQueue/examples/random_sleep.py" -p 1
python job_queue_client.py add "$HOME/anaconda3/envs/$env_name/bin/python" "$HOME/SharedJobsQueue/examples/random_sleep.py" -p low