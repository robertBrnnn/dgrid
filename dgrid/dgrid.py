"""
Author: Robert James Brennan
Email:  robert.brnnn@gmail.com

Root execution script for dgrid
"""

import argparse
from .version import __version__
from .scheduling.schedule import Job
from .scheduling.utils.logger import Logger


def main():
    """
    CLI for DGrid.
    :return:
    """
    # Build command line
    global logger
    parser = argparse.ArgumentParser(description='Command Line utility for executing batch tasks in Docker',
                                     add_help=False)

    required = parser.add_argument_group("Required arguments")

    required.add_argument('--dockdef',
                          dest='df',
                          help="Docker json definition file",
                          required=True)

    # Optional CLI arguments
    optional = parser.add_argument_group("Optional arguments")

    optional.add_argument('--hostfile',
                          dest='hf',
                          help="Hostfile to use for execution",
                          required=False)

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

    # Get required logger for use during execution
    logger = Logger(args.debug).get_logger()

    # Create job instance and execute
    job = Job(args.df, args.hf)
    job.execute()
