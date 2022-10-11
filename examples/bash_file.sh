if [ $# -eq 0 ]; then
    env_name=jobqueue
else
    env_name=$1
fi

$HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/random_sleep.py

echo "finished running the bash script!"