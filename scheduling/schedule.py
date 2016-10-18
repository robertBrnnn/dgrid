"""
Author: Robert Brennan
Email:  robert.brnnn@gmail.com

Calls methods to read the host file and docker definition file and return them as objects
Instantiates the required scheduler only, and returns it to calling script
"""

from utils import fileparser
from scheduling.schedulers import mapping


class Scheduler(object):

    def __init__(self, containers, hosts):
        self.containers = containers
        self.hosts = hosts

    @staticmethod
    def get_scheduler(scheduler, hosts, containers):
        # Import only the class of the scheduler we need -> no point in loading every scheduler
        scheduler_class = getattr(mapping, scheduler)

        module = __import__('scheduling.schedulers.' + scheduler_class, fromlist=scheduler_class)
        klass = getattr(module, scheduler_class)

        sched = klass(containers, hosts)

        # Return the scheduler
        return sched


def load_job(hostfile, dockerdef, scheduler):
    # Load the hostfile and containers into arrays
    # Create a scheduler using scheduler parameter
    containers, hosts = fileparser.load_data(dockerdef, hostfile)

    return Scheduler.get_scheduler(scheduler, hosts, containers)
