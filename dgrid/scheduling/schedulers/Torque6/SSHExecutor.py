"""
Author: Robert Brennan
SSH execution class for use with Torque 6, with cpu sets
"""

import logging
import os
import random
import socket
import string

from fabric.api import run
from fabric.tasks import execute
from dgrid.scheduling.utils.Errors import HostValueError, InteractiveContainerNotSpecified

from dgrid.conf import settings

logger = logging.getLogger(__name__)


class SSHExecutor:

    def __init__(self, containers, hosts):
        """
        :param containers: List of container objects
        :param hosts: list of hosts
        """
        self.hosts = hosts
        self.containers = containers
        # get hostname so we can differentiate when running containers, no need to ssh into current machine to execute
        self.hostname = socket.gethostname()
        self.int_container = None

        job_id = os.environ.get('PBS_JOB_ID')
        cgroups_dir = settings.cgroup_dir

        self.cpu_shares = ['cat', cgroups_dir + '/cpu/torque/' + job_id + '/cpu.shares']
        self.cpus = ['cat', cgroups_dir + '/cpuset/torque/' + job_id + '/cpuset.cpus']
        self.memory = ['cat', cgroups_dir + '/memory/torque/' + job_id + '/memory.limit_in_bytes']
        self.memory_swappiness = ['cat', cgroups_dir + '/memory/torque/' + job_id + '/memory.swappiness']
        self.memory_swap_limit = ['cat', cgroups_dir + '/memory/torque/' + job_id + '/memory.memsw.limit_in_bytes']
        self.kernel_memory_limit = ['cat', cgroups_dir + '/memory/torque/' + job_id + '/memory.kmem.limit_in_bytes']

        # Strip out current host from list
        try:
            logger.debug(self.hosts)
            self.hosts.remove(self.hostname)
            logger.debug(self.hosts)
        except ValueError:
            raise HostValueError('Hostname of execution host not in assigned hosts list')

        # Get the interactive container, and remove from list
        for container in self.containers:
            if container.interactive == 'True':
                self.int_container = container
                self.containers.remove(self.int_container)

        if self.int_container is None:
            raise InteractiveContainerNotSpecified('An interactive container must be specified for logging')

        self.containers_per_host = dict()

    def run(self):
        """
        For each container, select a host and run it there.
        After all hosts have been assigned a container, spin up interactive container locally
        :return: NULL
        """
        logger.debug('Assigning containers to hosts')
        for x in range(len(self.containers)):
            if isinstance(self.hosts, list):
                host = self.hosts[x]
            else:
                host = self.hosts
            container = self.containers[x]
            identity = execute(self.run_container, container, host=host)
            self.containers_per_host[host] = identity

    def run_container(self, container):
        """
        Gets the constraints placed on the container by Torque and assigns them to the container
        Runs the container after, constraints have been assigned
        :param container: Container to be run
        :return: Unique container ID
        """
        cpushares = run(' '.join(self.cpu_shares))
        cpus = run(' '.join(self.cpus))
        memory = run(' '.join(self.memory))
        memory_swappiness = run(' '.join(self.memory_swappiness))
        memory_swap_limit = run(' '.join(self.memory_swap_limit))
        kernel_memory = run(' '.join(self.kernel_memory_limit))

        container.cpu_shares = cpushares
        container.cpu_set = cpus
        container.memory = memory
        container.memory_swappiness = memory_swappiness
        container.memory_swap = memory_swap_limit
        container.kernel_memory = kernel_memory
        container.name += ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(20)])

        run(' '.join(container.run()))
        return container.name

    def checkpoint_containers(self):
        pass

    def setup_constraints(self):
        pass

    def restore(self):
        pass

    def cleanup(self):
        pass

    def terminate(self):
        pass
