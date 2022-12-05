# set -e 

if [ $# -eq 0 ]; then
    env_name=jobsqueue
else
    env_name=$1
fi


CMD="JobsClient add /bin/bash  $HOME/SharedJobsQueue/examples/bash_example.sh"
printf "\n# Add bash command\n"
echo $ $CMD
$CMD

CMD="JobsClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py"
printf "\n# Add python command\n"
echo $ $CMD
$CMD

CMD="JobsClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sleep_nsecs.py"
printf "\n# Add python command\n"
echo $ $CMD
$CMD

CMD="JobsClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/error_example.py"
printf "\n# Add error example command\n"
echo $ $CMD
$CMD

CMD="JobsClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py --mem 1e3"
printf "\n# Add command that requires gpu usage\n"
echo $ $CMD
$CMD

CMD="JobsClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py --mem 1e9"
printf "\n# Add command that requires gpu usage with dataparallel\n"
echo $ $CMD
$CMD

CMD="JobsClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py -p 4"
printf "\n# Add python command with urgent and high priority\n"
echo $ $CMD
$CMD

CMD="JobsClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py -p high"
echo $ $CMD
$CMD

CMD="JobsClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py -p 1"
printf "\n# Add python command with low priority\n"
echo $ $CMD
$CMD

CMD="JobsClient add $HOME/anaconda3/envs/$env_name/bin/python $HOME/SharedJobsQueue/examples/sucess_example.py -p low"
echo $ $CMD
$CMD

CMD="JobsClient"
printf "\n# Show current job queue\n"
echo $ $CMD
$CMD

CMD="JobsClient show-state waiting"
printf "\n# Show waiting jobs\n"
echo $ $CMD
$CMD

CMD="JobsClient unpause ids 0 1 2"
printf "\n# Resume jobs with ids 0, 1 and 2\n"
echo $ $CMD
$CMD

CMD="JobsClient show-state waiting"
printf "\n# Show waiting jobs\n"
echo $ $CMD
$CMD


CMD="JobsClient remove 1 4"
printf "\n# Remove job with id=1 and id=4 from queue\n"
echo $ $CMD
$CMD

CMD="JobsClient update 5 priority 4"
printf "\n# Update job(id=5) priority to urgent\n"
echo $ $CMD
$CMD

CMD="JobsClient update 5 priority normal"
printf "\n# Update job(id=5) priority to normal\n"
echo $ $CMD
$CMD


CMD="JobsClient clear-state error "
printf "\n# Remove jobs that errored\n"
echo $ $CMD
$CMD

CMD="JobsClient clear "
printf "\n# Remove all jobs\n"
echo $ $CMD
$CMD

CMD="JobsClient clear -y"
printf "\n# Remove all jobs\n"
echo $ $CMD
$CMD


CMD="JobsClient"
printf "\n# Show current job queue\n"
echo $ $CMD
$CMD