"""
Author: Robert Brennan
SSH execution class for use with Torque 6, with cpu sets
"""

import logging
import os
import random
import socket
import string
from subprocess import Popen, PIPE

from fabric.api import run, env
from fabric.tasks import execute
from dgrid.scheduling.utils.Errors import HostValueError, InteractiveContainerNotSpecified, RemoteExecutionError

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

        self.job_id = os.environ.get('PBS_JOB_ID')
        cgroups_dir = settings.cgroup_dir

        self.cpu_shares = ['cat', cgroups_dir + '/cpu/torque/'
                           + self.job_id + '/cpu.shares']

        self.cpus = ['cat', cgroups_dir + '/cpuset/torque/'
                     + self.job_id + '/cpuset.cpus']

        self.memory = ['cat', cgroups_dir + '/memory/torque/'
                       + self.job_id + '/memory.limit_in_bytes']

        self.memory_swappiness = ['cat', cgroups_dir + '/memory/torque/'
                                  + self.job_id + '/memory.swappiness']

        self.memory_swap_limit = ['cat', cgroups_dir + '/memory/torque/'
                                  + self.job_id + '/memory.memsw.limit_in_bytes']

        self.kernel_memory_limit = ['cat', cgroups_dir + '/memory/torque/'
                                    + self.job_id + '/memory.kmem.limit_in_bytes']

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

        self.local_run = False
        self.local_pid = None
        # Get Fabric to throw an RemoteExecutionError when remote commands fail, instead of aborting
        env.abort_exception = RemoteExecutionError

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

            try:
                execute(self.run_container, container, host=host)
                container.execution_host = host
            except RemoteExecutionError as rex:
                logger.critical("Remote execution of containers failed: ", rex.message)
                self.terminate_clean()

        try:
            self.run_int_container()
        except Exception as ex:
            '''
            Need to catch any exception thrown during local execution, so using general exception class.
            For any error, we assume termination, as it is likely an issue with submitters container.
            '''
            logger.critical("Interactive container execution error: ", ex.message)
            self.terminate_clean()

        # Stop all containers. Remove all containers.
        self.terminate_clean()
        self.remove_images()

    def run_container(self, container):
        """
        Gets the constraints placed on the container by Torque and assigns them to the container
        Runs the container after, constraints have been assigned
        :param container: Container to be run
        :return: Null
        """
        cpushares = run(' '.join(self.cpu_shares))
        cpus = run(' '.join(self.cpus))
        memory = run(' '.join(self.memory))
        memory_swappiness = run(' '.join(self.memory_swappiness))
        memory_swap_limit = run(' '.join(self.memory_swap_limit))
        kernel_memory = run(' '.join(self.kernel_memory_limit))

        container.cpu_shares = cpushares
        container.cpu_set = cpus
        container.memory = memory + "b"
        container.memory_swappiness = memory_swappiness
        container.memory_swap = memory_swap_limit + "b"
        container.kernel_memory = kernel_memory + "b"
        container.name += ''.join([random.choice(string.ascii_letters + string.digits) for n in range(20)])

        run(' '.join(container.run()) +
            " && pbs_track -j %i -a $(docker inspect --format '{{ .State.Pid }}' %s)"
            % (int(self.job_id), container.name))

    def run_int_container(self):
        """
        Runs the interactive container on the host where the job was spawned
        :return: Null
        """
        # Setup CGroup constraints set by torque
        self.setup_constraints()

        # Randomise the containers name
        self.int_container.name += ''.join([random.choice(string.ascii_letters + string.digits) for n in range(20)])

        proc = Popen(self.int_container.run(), stdout=PIPE, stderr=PIPE)
        self.local_run = True
        self.local_pid = proc.pid
        logger.debug("Local process id: " + str(self.local_pid))

        while proc.poll() is None:
            l = proc.stdout.readline()
            l += proc.stderr.readline()
            logger.info(l)

        logger.info(proc.stdout.read())
        self.local_run = False

    def setup_constraints(self):
        """
        Gets the constraints set by Torque for the job on current host
        Assigns the values to the interactive container
        :return: Null
        """
        cpushares = Popen(self.cpu_shares, stdout=PIPE)
        cpus = Popen(self.cpus, stdout=PIPE)
        memory = Popen(self.memory, stdout=PIPE)
        memory_swappiness = Popen(self.memory_swappiness, stdout=PIPE)
        memory_swap_limit = Popen(self.memory_swap_limit, stdout=PIPE)
        kernel_memory = Popen(self.kernel_memory_limit, stdout=PIPE)

        self.int_container.cpu_shares = cpushares.stdout.read().replace("\n", "")
        self.int_container.cpu_set = cpus.stdout.read().replace("\n", "")
        self.int_container.memory = memory.stdout.read().replace("\n", "") + "b"
        self.int_container.memory_swappiness = memory_swappiness.stdout.read().replace("\n", "")
        self.int_container.memory_swap = memory_swap_limit.stdout.read().replace("\n", "") + "b"
        self.int_container.kernel_memory = kernel_memory.stdout.read().replace("\n", "") + "b"

    def terminate_clean(self):
        """
        Iterates through all remote containers and runs 'docker stop <container>' on each remote.
        :return: Null
        """
        logger.debug("stopping and removing remote containers")
        for container in self.containers:
            if container.execution_host is not None:
                command = ' '.join(container.terminate()) + " && " + ' '.join(container.cleanup())
                execute(self.execute_remote, command, host=container.execution_host)

        # Check if local interactive container is still running
        if self.local_run is True:
            Popen('kill -9 ' + self.local_pid)

        # Remove the interactive container
        Popen(self.int_container.cleanup(), stdout=PIPE)

    def remove_images(self):
        if settings.image_cleanup == 1:
            command = "DANGLING_IMAGES=$(docker images -qf \"dangling=true\") && " \
                      "if [[ -n $DANGLING_IMAGES ]]; then docker rmi \"$DANGLING_IMAGES\"; fi && " \
                      "USED_IMAGES=($(docker ps -a --format '{{.Image}}'" \
                      " | sort -u | uniq | awk -F ':' '$2{print $1\":\"$2}!$2{print $1\":latest\"}')) && " \
                      "ALL_IMAGES=($(docker images --format '{{.Repository}}:{{.Tag}}' | sort -u )) && " \
                      "for i in \"${ALL_IMAGES[@]}\"; do UNUSED=true; " \
                      "for j in \"${USED_IMAGES[@]}\"; " \
                      "do if [[ \"$i\" == \"$j\" ]]; " \
                      "then UNUSED=false; " \
                      "fi done; " \
                      "if [[ \"$UNUSED\" == true ]]; " \
                      "then docker rmi \"$i\"; " \
                      "fi done"

            for container in self.containers:
                if container.execution_host is not None:
                    execute(self.execute_remote, command, host=container.execution_host)

            Popen(command)

        if settings.image_cleanup == 2:
            for container in self.containers:
                if container.execution_host is not None:
                    execute(self.execute_remote, container.image_cleanup, host=container.execution_host)

            if self.local_pid is not None:
                Popen(self.int_container.image_cleanup)

    def execute_remote(self, command):
        """
        Task that executes a given command on remote host
        :param command: Command to execute
        :return: Null
        """
        run(command)

    def checkpoint_containers(self):
        pass

    def restore(self):
        pass
