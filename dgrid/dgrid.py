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
from .scheduling.utils.logger_ltf import LessThanFilter


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
                          help="Hostfile to use for execution",
                          required=True)

    required.add_argument('--dockdef',
                          dest='df',
                          help="Docker json definition file",
                          required=True)

    # Optional CLI arguments
    optional = parser.add_argument_group("Optional arguments")
    optional.add_argument('-h',
                          '--help',
                          help="Display this help message and exit",
                          action='help')

    optional.add_argument('-v',
                          '--version',
                          action='version',
                          help="Display program's version number and exit",
                          version=__version__)

    # Optional debug parameter, for verbose output during execution
    optional.add_argument('--enable-debug',
                          dest='debug',
                          action='store_true',
                          help="Enable debug logging during execution")
    # Set default value of debug to False
    parser.set_defaults(debug=False)
    args = parser.parse_args()

    # If DEBUG is enabled in settings, or on command line, enable debug logging. Otherwise INFO logging
    if settings.DEBUG or args.debug:
        logger = logging.getLogger()
        logger.setLevel(logging.NOTSET)

        logging_handler_out = logging.StreamHandler(sys.stdout)
        logging_handler_out.setLevel(logging.DEBUG)
        logging_handler_out.addFilter(LessThanFilter(logging.WARNING))
        logger.addHandler(logging_handler_out)

        logging_handler_err = logging.StreamHandler(sys.stderr)
        logging_handler_err.setLevel(logging.WARNING)
        logger.addHandler(logging_handler_err)
    else:
        logger = logging.getLogger()
        logger.setLevel(logging.NOTSET)

        logging_handler_out = logging.StreamHandler(sys.stdout)
        logging_handler_out.setLevel(logging.INFO)
        logging_handler_out.addFilter(LessThanFilter(logging.WARNING))
        logger.addHandler(logging_handler_out)

        logging_handler_err = logging.StreamHandler(sys.stderr)
        logging_handler_err.setLevel(logging.WARNING)
        logger.addHandler(logging_handler_err)

    execute_job(args.hf, args.df)
