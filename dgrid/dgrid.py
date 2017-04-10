"""
Author: Robert James Brennan
Email:  robert.brnnn@gmail.com

Root execution script for dgrid

    Copyright (C) 2017  Robert James Brennan
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
