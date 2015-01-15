# This won't work for interactive shells
source `dirname $0`/common.sh
#source common.sh

# This script holds some common functions and variables for the run_training_*
# scripts.

# there is one physical socket, but two physical cores and four virtual cores
# so run twice as many jobs as we have sockets
RETRIES=3
#PARALLEL_OPTS="--use-cpus-instead-of-cores --retries $RETRIES --halt-on-error 1 --nice 19 --progress --ctrlc --files --env PATH"
# --compress may seem beneficial, but it tends to hang the jobs forever
# Remember: 10.0.0.7 is a test box
# From the man page:
# 0: Do not halt if a job fails. Exit status will be the number of jobs failed. This is the default.
# 1: Do not start new jobs if a job fails, but complete the running jobs including cleanup. The exit status will be the exit status from the last failing job.
# 2: Kill off all jobs immediately and exit without cleanup. The exit status will be the exit status from the failing job.
HALT_ON_ERR=1


PARALLEL_OPTS="--use-cpus-instead-of-cores --retries $RETRIES --nice 19"
PARALLEL_OPTS="${PARALLEL_OPTS} --progress --ctrlc --files --env PATH"
PARALLEL_OPTS="${PARALLEL_OPTS} --env PYTHONPATH --env VIRTUAL_ENV --halt-on-error $HALT_ON_ERR"
#HOSTS="10.0.0.3,10.0.0.4,10.0.0.5,10.0.0.8,10.0.0.9,10.0.0.10,10.0.0.11,10.0.0.14,10.0.0.15,10.0.0.16,10.0.0.17,10.0.0.18,10.0.0.19,10.0.0.20,10.0.0.21,10.0.0.22,10.0.0.23,10.0.0.24,10.0.0.27"
HOSTS="2/10.0.0.3,2/10.0.0.4,2/10.0.0.5,2/10.0.0.6,2/10.0.0.8,2/10.0.0.9,2/10.0.0.10,2/10.0.0.11,2/10.0.0.12,2/10.0.0.13,2/10.0.0.14,2/10.0.0.15,2/10.0.0.16,2/10.0.0.17,2/10.0.0.18,2/10.0.0.19,2/10.0.0.20,2/10.0.0.21,2/10.0.0.22,2/10.0.0.23,2/10.0.0.24,2/10.0.0.25,2/10.0.0.26,2/10.0.0.27,2/10.0.0.28,2/10.0.0.29,2/10.0.0.30,2/10.0.0.31"
# gillespie is full right now
EXTRA_HOSTS="6/gillespie" # ,10/ella"
POOL_HOSTS=$HOSTS
HOSTS=$HOSTS #,$EXTRA_HOSTS

function open_connections() {
    HOSTS=""
    HOSTLIST=""
    for box in `seq 02 31`; do
        ping -c 1 10.0.0.$box && HOSTS=${HOSTS}10.0.0.$box"," \
            && ssh -X -f  10.0.0.$box /usr/bin/xterm &&  screen -d -m ssh 10.0.0.$box;
        
    done
    echo $HOSTS
}

