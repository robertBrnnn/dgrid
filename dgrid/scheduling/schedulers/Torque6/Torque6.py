"""
Author: Robert Brennan
Email:  robert.brnnn@gmail.com

Implementation for docker execution on Torque 6.X series

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

import logging

from dgrid.scheduling.schedule import Scheduler
from dgrid.scheduling.schedulers.Torque6.SSHExecutor import SSHExecutor

from dgrid.conf import settings

logger = logging.getLogger(__name__)


class Torque6(Scheduler):
    """
    Implementation of scheduler class for Torque6
    """
    def __init__(self, containers, hosts=None):
        Scheduler.__init__(self, containers, hosts)
        self.containers = containers
        self.hosts = hosts

        # Get execution parameter, default to SSH
        exec_method = getattr(settings, 'Execution_Method', 'SSH')
        if exec_method.upper() == 'SSH':
            logger.debug('Loading SSH executor')
            self.executor = SSHExecutor(self.containers, self.hosts)

    def run_job(self):
        """
        Called to run the Docker job
        :return:
        """
        self.executor.run()

    def checkpoint(self):
        """
        Called to checkpoint containers of the job
        :return:
        """
        self.executor.checkpoint()

    def restore(self):
        """
        Called to restore container of the job
        :return:
        """
        self.executor.restore()

    def terminate(self):
        """
        Called to terminate containers of the job
        :return:
        """
        logger.debug("Terminate called")
        self.executor.terminate_clean()
        logger.debug("Remove images")
        self.executor.remove_images()
