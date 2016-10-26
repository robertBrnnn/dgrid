"""
Author: Robert Brennan
Email:  robert.brnnn@gmail.com

Implementation for docker execution on Torque 6.X series
"""

from scheduling.schedule import Scheduler
from conf import settings
import socket


class Torque6(Scheduler):
    def __init__(self, containers, hosts):
        Scheduler.__init__(self, containers, hosts)
        self.containers = containers
        self.hosts = hosts
        # get hostname so we can differentiate when running containers, no need to ssh into current machine to execute
        self.hostname = socket.gethostname()

    def run_job(self):
        pass

    def checkpoint(self):
        pass

    def restore(self):
        pass

    def terminate(self):
        pass

    def cleanup(self):
        pass
