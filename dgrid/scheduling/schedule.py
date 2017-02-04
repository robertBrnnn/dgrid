"""
Author: Robert Brennan
Email:  robert.brnnn@gmail.com

Calls methods to read the host file and docker definition file and return them as objects
Instantiates the required scheduler only, and returns it to calling script
"""

import logging
import sys
import signal

from abc import ABCMeta, abstractmethod
from dgrid.conf import settings
from dgrid.scheduling.utils import fileparser

logger = logging.getLogger(__name__)


class Scheduler(object):
    # abstract class reference docs.python.org/2/library/abc.html
    __metaclass__ = ABCMeta

    def __init__(self, containers, hosts):
        self.containers = containers
        self.hosts = hosts

    @abstractmethod
    def run_job(self):
        """
        Called to run a given job description
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def checkpoint(self):
        """
        Called to checkpoint containers of a given job
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def restore(self):
        """
        Called to restore containers of a given job
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def terminate(self):
        """
        Called to terminate all container of a given job
        :return:
        """
        raise NotImplementedError

    def get_scheduler(hosts, containers):
        """
        Instantiates the relevant scheduler, with container list and host list
        :param hosts: Array containing all hosts assigned to the job
        :param containers: Array containing all containers for the job
        :return: Required scheduler
        """
        # Import only the class of the scheduler we need -> no point in loading every scheduler
        scheduler_class = settings.scheduler

        try:
            # module importing from stackoverflow.com/a/547867/4345813
            logger.debug('Loading scheduler class %s', scheduler_class)
            module = __import__('dgrid.scheduling.schedulers.' + scheduler_class + '.'
                                + scheduler_class, fromlist=scheduler_class)

            klass = getattr(module, scheduler_class)
            sched = klass(containers, hosts)

            # Return the scheduler
            return sched
        except ImportError:
            logger.error("No Scheduler named %s. Check configuration files." % scheduler_class)
            sys.exit(1)

    get_scheduler = staticmethod(get_scheduler)


class Job:
    def __init__(self, hostfile, dockerfile):
        self.hf = hostfile
        self.df = dockerfile
        self.job = None

    def termination_handler(self, signum, frame):
        # Handle termination signal from here, call terminate method of instantiated scheduler
        logger.info('Pre-Termination signal received, terminating running containers')
        self.job.terminate()
        sys.exit(0)

    def checkpoint_handler(self, signum, frame):
        logger.info('Checkpoint signal received, running checkpoint on selected containers')
        self.job.checkpoint()
        sys.exit(0)

    def execute(self):
        """
        Sets up job. Creates termination and checkpoint handlers if configured
        Runs the task
        :return:
        """

        # Create executor instance
        self.load()

        # Setup termination and checkpoint handlers
        if hasattr(settings, 'termination_signal'):
            signal.signal(settings.termination_signal, self.termination_handler)

        if hasattr(settings, 'checkpoint_signal'):
            signal.signal(settings.checkpoint_signal, self.checkpoint_handler)

        # Run the task
        self.job.run_job()

    def load(self):
        """
        Sets up scheduler class, for running the job, loads into class attribute job.
        :return:
        """
        self.job = load_job(self.hf, self.df)


def load_job(hostfile, dockerdef):
    """
    Loads the containers and hosts from their relevant files into arrays, and returns the required scheduler
    :param hostfile: Hostfile for the job
    :param dockerdef: Json docker definition file
    :return: Required scheduler
    """
    containers, hosts = fileparser.load_data(dockerdef, hostfile)

    return Scheduler.get_scheduler(hosts, containers)
