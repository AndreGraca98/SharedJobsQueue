if [ $# -eq 0 ]; then
    env_name=jobqueue
else
    env_name=$1
fi


JobQueueClient(){
    $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/jobs_queue/client.py "$@"
}


# TODO: Update this example

echo ""
echo "# Add bash command"
echo "$ JobQueueClient add /bin/bash $HOME/SharedJobsQueue/examples/file.sh"
JobQueueClient add /bin/bash $HOME/SharedJobsQueue/examples/file.sh

echo ""
echo "# Add python command"
echo "$ JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py"
JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py

echo "$ JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sleep_nsecs.py"
JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sleep_nsecs.py

echo ""
echo "# Add error example command"
echo "$ JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/error_example.py"
JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/error_example.py

echo ""
echo "# Add command that requires gpu usage"
echo "$ JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py --mem 1e3"
JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py --mem 1e3

echo ""
echo "# Add python command with urgent and high priority"
echo "$ JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py --mem 1e9 -p 4"
JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py --mem 1e9 -p 4

echo "$ JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py -p 3"
JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py -p 3

echo ""
echo "# Add python command with low priority"
echo "$ JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py"
JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py -p 1

echo "$ JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py -p low"
JobQueueClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py -p low

echo ""
echo "# Show current job queue"
echo "$ JobQueueClient"
JobQueueClient

# echo ""
# echo "# Remove job with id=1 and id=4 from queue"
# echo "$ JobQueueClient remove 1 4"
# JobQueueClient remove 1 4

echo ""
echo "# Update job(id=5) priority to urgent"
echo "$ JobQueueClient update 5 priority 4"
JobQueueClient update 5 priority 4

echo ""
echo "# Update job(id=5) priority to normal"
echo "$ JobQueueClient update 5 priority normal"
JobQueueClient update 5 priority normal

# echo ""
# echo "# Remove all jobs"
# echo "$ JobQueueClient clear "
# JobQueueClient clear

# echo "$ JobQueueClient clear -y"
# JobQueueClient clear -y
