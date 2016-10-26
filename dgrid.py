"""
Author: Robert James Brennan
Email:  robert.brnnn@gmail.com

Root execution script for dgrid
"""

import argparse
import signal
from scheduling.schedule import load_job


def termination_handler(signum, frame):
    # Handle termination signal from here, call terminate method of instantiated scheduler
    print 'Pre-Termination signal received, checkpointing running containers'


def execute_job():
    job = load_job(args.hf, args.df)
    job.run_job()

if __name__ == '__main__':
    # Build command line
    parser = argparse.ArgumentParser(description='Command Line utility for executing batch tasks in Docker')

    parser.add_argument('--hostfile',
                        dest='hf',
                        help="Hostfile to use for execution",
                        required=True)

    parser.add_argument('--dockdef',
                        dest='df',
                        help="Docker json definition file",
                        required=True)

    # This could be st in settings file as well, leave here for now
    parser.add_argument('--termsig',
                        dest='sig',
                        help="Integer value of signal to be passed to process pre termination")

    # Job id will be needed for Torque
    parser.add_argument('--job-id',
                        dest='jobid',
                        help="ID assigned to job by scheduler")
    args = parser.parse_args()

    execute_job()

    # Lets assume it'll be SIGHUP for now...
    signal.signal(signal.SIGHUP, termination_handler)
