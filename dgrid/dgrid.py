"""
Author: Robert James Brennan
Email:  robert.brnnn@gmail.com

Root execution script for dgrid
"""

import argparse
import logging
import signal
from conf import settings
from scheduling.schedule import load_job


def termination_handler(signum, frame):
    # Handle termination signal from here, call terminate method of instantiated scheduler
    print 'Pre-Termination signal received, checkpointing running containers'


def execute_job(hf, df):
    job = load_job(hf, df)
    job.run_job()


def main():
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

    args = parser.parse_args()

    if settings.DEBUG:
        logging.basicConfig(format='%(levelname)s [%(name)s] : %(message)s  %(asctime)s', level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        logger.debug('Debug logging started')
    else:
        logging.basicConfig(format='%(levelname)s:%(message)s  %(asctime)s', level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info('Logging started')

    # Retrieve the termination signal from the settings file
    signal.signal(settings.termination_signal, termination_handler)

    execute_job(args.hf, args.df)
