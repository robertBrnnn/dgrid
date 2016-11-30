"""
Author: Robert James Brennan
Email:  robert.brnnn@gmail.com

Root execution script for dgrid
"""

import argparse
import logging
import signal
import sys
from functools import partial
from .version import __version__
from .conf import settings
from .scheduling.schedule import load_job


def termination_handler(job, signum, frame):
    # Handle termination signal from here, call terminate method of instantiated scheduler
    logger.info('Pre-Termination signal received, checkpointing running containers')
    job.terminate()
    sys.exit(0)


def execute_job(hf, df):
    job = load_job(hf, df)
    # Create signal handler and send job object to termination handler
    signal.signal(settings.termination_signal, partial(termination_handler, job))
    job.run_job()
    sys.exit(0)


def main():
    # Build command line
    global logger
    parser = argparse.ArgumentParser(description='Command Line utility for executing batch tasks in Docker',
                                     add_help=False)

    required = parser.add_argument_group("Required arguments")

    required.add_argument('--hostfile',
                          dest='hf',
                          help="Hostfile to use for execution")

    required.add_argument('--dockdef',
                          dest='df',
                          help="Docker json definition file")

    # Optional CLI arguments
    optional = parser.add_argument_group("Optional arguments")
    optional.add_argument('-h',
                          '--help',
                          help="Display this help message and exit",
                          action='help')

    optional.add_argument('-v',
                          '--version',
                          dest='version',
                          help="Print version of DGrid",
                          action='store_true')

    # Optional debug parameter, for verbose output during execution
    optional.add_argument('--enable-debug',
                          dest='debug',
                          action='store_true',
                          help="Enable debug logging during execution")
    # Set default value of debug to False
    parser.set_defaults(debug=False, version=False)
    args = parser.parse_args()

    if args.version:
        print("DGrid version " + __version__)
        sys.exit(0)

    if args.hf is None or args.df is None:
        sys.exit("One or more required arguments missing. Run 'dgrid -h' to see help message")

    # If DEBUG is enabled in settings, or on command line, enable debug logging. Otherwise INFO logging
    if settings.DEBUG or args.debug:
        logging.basicConfig(format='%(levelname)s [%(name)s] : %(message)s  %(asctime)s',
                            level=logging.DEBUG,
                            stream=sys.stdout)
        logger = logging.getLogger(__name__)
        logger.debug('Debug logging started')
    else:
        logging.basicConfig(format='%(message)s  %(asctime)s',
                            level=logging.INFO,
                            stream=sys.stdout)
        logger = logging.getLogger(__name__)

    execute_job(args.hf, args.df)
