"""
Author: Robert Brennan
Email:  robert.brnnn@gmail.com

Calls methods to read the host file and docker definition file and return them as objects
Instantiates the required scheduler only, and returns it to calling script
"""

import logging

from dgrid.conf import settings
from dgrid.scheduling.utils import fileparser

logger = logging.getLogger(__name__)


class Scheduler(object):

    def __init__(self, containers, hosts):
        self.containers = containers
        self.hosts = hosts

    @staticmethod
    def get_scheduler(hosts, containers):
        """
        Instantiates the relevant scheduler, with container list and host list
        :param hosts: Array containing all hosts assigned to the job
        :param containers: Array containing all containers for the job
        :return: Required scheduler
        """
        # Import only the class of the scheduler we need -> no point in loading every scheduler
        scheduler_class = settings.scheduler

        logger.debug('Loading scheduler class %s', scheduler_class)
        module = __import__('dgrid.scheduling.schedulers.' + scheduler_class + '.'
                            + scheduler_class, fromlist=scheduler_class)

        klass = getattr(module, scheduler_class)
        sched = klass(containers, hosts)

        # Return the scheduler
        return sched


def load_job(hostfile, dockerdef):
    """
    Loads the containers and hosts from their relevant files into arrays, and returns the required scheduler
    :param hostfile: Hostfile for the job
    :param dockerdef: Json docker definition file
    :return: Required scheduler
    """
    containers, hosts = fileparser.load_data(dockerdef, hostfile)

    return Scheduler.get_scheduler(hosts, containers)
