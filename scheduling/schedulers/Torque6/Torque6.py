"""
Author: Robert Brennan
Email:  robert.brnnn@gmail.com

Implementation for docker execution on Torque 6.X series
"""

from scheduling.schedule import Scheduler
from scheduling.schedulers.Torque6.SSHExecutor import SSHExecutor
from conf import settings
import socket
import logging

logger = logging.getLogger(__name__)


class Torque6(Scheduler):
    def __init__(self, containers, hosts):
        Scheduler.__init__(self, containers, hosts)
        self.containers = containers
        self.hosts = hosts

        # Get execution parameter, default to SSH
        exec_method = getattr(settings, 'Execution_Method', 'SSH')
        if exec_method.upper() == 'SSH':
            logger.debug('Loading SSH executor')
            self.executor = SSHExecutor(self.containers, self.hosts)

    def run_job(self):
        self.executor.run()

    def checkpoint(self):
        pass

    def restore(self):
        pass

    def terminate(self):
        pass

    def cleanup(self):
        pass
