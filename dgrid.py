"""
Author: Robert James Brennan
Email:  robert.brnnn@gmail.com

Root execution script for dgrid
"""

import argparse
import signal
from scheduling.schedule import load_job
from conf import settings


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

    # Job id will be needed for Torque
    parser.add_argument('--job-id',
                        dest='jobid',
                        help="ID assigned to job by scheduler")
    args = parser.parse_args()

    execute_job()

    # Retrieve the termination signal from the settings file
    signal.signal(getattr(settings, 'termination_signal'), termination_handler())
