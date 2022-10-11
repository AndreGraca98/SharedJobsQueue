if [ $# -eq 0 ]; then
    env_name=jobqueue
else
    env_name=$1
fi


folder_name=$HOME/SharedJobsQueue


python $folder_name/job_queue_client.py add "$HOME/anaconda3/envs/$env_name/bin/python" "$folder_name/examples/random_sleep.py" -p high
python $folder_name/job_queue_client.py add "$HOME/anaconda3/envs/$env_name/bin/python" "$folder_name/examples/random_sleep.py"
python $folder_name/job_queue_client.py add "$HOME/anaconda3/envs/$env_name/bin/python" "$folder_name/examples/random_sleep.py" -p urgent
python $folder_name/job_queue_client.py add "$HOME/anaconda3/envs/$env_name/bin/python" "$folder_name/examples/random_sleep.py"
python $folder_name/job_queue_client.py add "$HOME/anaconda3/envs/$env_name/bin/python" "$folder_name/examples/random_sleep.py" -p urgent
python $folder_name/job_queue_client.py add "$HOME/anaconda3/envs/$env_name/bin/python" "$folder_name/examples/random_sleep.py" -p low
python $folder_name/job_queue_client.py add "$HOME/anaconda3/envs/$env_name/bin/python" "$folder_name/examples/random_sleep.py" -p 1
python $folder_name/job_queue_client.py add "$HOME/anaconda3/envs/$env_name/bin/python" "$folder_name/examples/random_sleep.py" -p low