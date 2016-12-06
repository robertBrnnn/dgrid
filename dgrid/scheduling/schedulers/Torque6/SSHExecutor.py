"""
Author: Robert Brennan
SSH execution class for use with Torque 6, with cpu sets
"""

import logging
import os
import sys
import random
import socket
import string
import re
from subprocess import Popen, PIPE
from fabric.api import run, env
from fabric.tasks import execute
from fabric.network import disconnect_all
from dgrid.scheduling.utils.Errors import HostValueError, InteractiveContainerNotSpecified, RemoteExecutionError
from dgrid.scheduling.utils.docker_netorking import add_networking

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

        self.user = os.popen("id -u $USER").read().replace("\n", "")
        self.job_id = os.environ.get('PBS_JOBID')
        self.work_dir = os.environ.get("PBS_O_WORKDIR")

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

        context = os.path.realpath(__file__)
        path = re.sub('dgrid/scheduling/schedulers/Torque6/SSHExecutor\.py.*', "", context)
        self.script_dir = path + "/dgrid-scripts/"
        logger.debug("script directory is: " + self.script_dir)

        # Strip out current host from list
        try:
            logger.debug(self.hosts)
            self.hosts.remove(self.hostname)
            logger.debug(self.hosts)
        except ValueError:
            raise HostValueError('Hostname of execution host not in assigned hosts list')

        # The method add_networking will randomise container names.
        # If networking has been defined by the user,env variables, volumes mapping required will be added to container
        self.containers, self.create_net = add_networking(self.containers, self.work_dir)
        self.network_name = ""

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
        if self.create_net:
            logger.debug("creating docker container network for job")
            self.network_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(10)])
            self.docker_network(create=True, remove=False)

        logger.debug('Assigning containers to hosts')
        for x in range(len(self.containers)):
            try:
                if isinstance(self.hosts, list):
                    host = self.hosts[x]
                else:
                    host = self.hosts
            except IndexError:
                logger.critical("Not enough hosts assigned to job. One host per container is required")
                self.terminate_clean()
                self.remove_images()
                sys.exit("Terminating")

            container = self.containers[x]
            container.network = self.network_name if self.create_net else None

            try:
                logger.debug("Running remote containers")
                container.execution_host = host
                logger.debug("Setting user to " + str(self.user))
                container.user = str(self.user)
                execute(self.run_container, container, host=host)
            except RemoteExecutionError as rex:
                logger.critical("Remote execution of containers failed: " + rex.message)
                self.terminate_clean()
                self.remove_images()
                sys.exit("Terminating")
            finally:
                disconnect_all()

        try:
            self.run_int_container()
        except Exception as ex:
            '''
            Need to catch any exception thrown during local execution, so using general exception class.
            For any error, we assume termination, as it is likely an issue with submitters container.
            '''
            logger.critical("Interactive container execution error: " + ex.message)
            self.terminate_clean()
            self.remove_images()
            sys.exit("Terminating")

        try:
            self.terminate_clean()
        except RemoteExecutionError as rex:
            logger.error("Termination of containers failed")
            sys.exit("Aborting")

        try:
            self.remove_images()
        except RemoteExecutionError:
            logger.error("Image removal failed")
            sys.exit("Aborting")

        sys.exit(0)

    def docker_network(self, create=False, remove=False):
        """
        Creates or removes a docker network
        :param create: boolean parameter, defines whether docker network should be created
        :param remove: boolean parameter, defines whether docker network should be destroyed
        :return:
        """
        command = []
        if create:
            command = ['docker', 'network', 'create', '--driver=overlay', self.network_name]
        if remove:
            command = ['docker', 'network', 'rm', self.network_name]

        proc = Popen(command, stdout=PIPE, stderr=PIPE)
        for line in iter(proc.stdout.readline, ''):
            logger.info(line)
        for line in iter(proc.stderr.readline, ''):
            logger.error(line)

    def run_container(self, container):
        """
        Gets the constraints placed on the container by Torque and assigns them to the container
        Runs the container after, constraints have been assigned
        :param container: Container to be run
        :return: Null
        """
        cpushares = run(' '.join(self.cpu_shares))
        cpus = run(' '.join(self.cpus))
        container.cpu_shares = cpushares
        container.cpu_set = cpus

        if settings.enforce_memory_limits:
            memory = run(' '.join(self.memory))
            memory_swappiness = run(' '.join(self.memory_swappiness))
            memory_swap_limit = run(' '.join(self.memory_swap_limit))
            kernel_memory = run(' '.join(self.kernel_memory_limit))

            container.memory = memory + "b"
            container.memory_swappiness = memory_swappiness
            container.memory_swap = memory_swap_limit + "b"
            container.kernel_memory = kernel_memory + "b"

        run(" ".join(container.run()))
        container_id = run("docker inspect --format '{{ .State.Pid }}' %s" % container.name)
        run("pbs_track -j %s -a '%s'" % (self.job_id, container_id))

    def run_int_container(self):
        """
        Runs the interactive container on the host where the job was spawned
        :return: Null
        """
        # Setup CGroup constraints set by torque
        self.setup_constraints()

        # Pull the image first
        # Image pulling during docker run sends to stdout
        result = Popen(["docker", "pull", self.int_container.image], stdout=PIPE, stderr=PIPE)
        for line in iter(result.stdout.readline, ''):
            logger.info(line)
        for line in iter(result.stderr.readline, ''):
            logger.error(line)

        # Add created docker network to container
        if self.create_net:
            self.int_container.network = self.network_name

        # Run the interactive container
        logger.debug(" ".join(self.int_container.run()))
        proc = Popen(self.int_container.run(), stdout=PIPE, stderr=PIPE)
        self.local_run = True
        self.local_pid = proc.pid
        logger.debug("Local process id: " + str(self.local_pid))

        for line in iter(proc.stdout.readline, ''):
            logger.info(line)

        for line in iter(proc.stderr.readline, ''):
            logger.error(line)

        self.local_run = False

    def setup_constraints(self):
        """
        Gets the constraints set by Torque for the job on current host
        Assigns the values to the interactive container
        :return: Null
        """
        cpushares = Popen(self.cpu_shares, stdout=PIPE)
        cpus = Popen(self.cpus, stdout=PIPE)
        self.int_container.cpu_shares = cpushares.stdout.read().replace("\n", "")
        self.int_container.cpu_set = cpus.stdout.read().replace("\n", "")

        if settings.enforce_memory_limits:
            memory = Popen(self.memory, stdout=PIPE)
            memory_swappiness = Popen(self.memory_swappiness, stdout=PIPE)
            memory_swap_limit = Popen(self.memory_swap_limit, stdout=PIPE)
            kernel_memory = Popen(self.kernel_memory_limit, stdout=PIPE)

            self.int_container.memory = memory.stdout.read().replace("\n", "") + "b"
            self.int_container.memory_swappiness = memory_swappiness.stdout.read().replace("\n", "")
            self.int_container.memory_swap = memory_swap_limit.stdout.read().replace("\n", "") + "b"
            self.int_container.kernel_memory = kernel_memory.stdout.read().replace("\n", "") + "b"

    def terminate_clean(self):
        """
        Iterates through all remote containers and runs 'docker stop <container>' on each remote.
        :return: Null
        """
        # Check if local interactive container is still running
        if self.local_run is True:
            terminate = Popen(self.int_container.terminate(), stdout=PIPE, stderr=PIPE)
            for line in iter(terminate.stdout.readline, ''):
                logger.info(line)
            for line in iter(terminate.stderr.readline, ''):
                logger.error(line)

        # Remove the interactive container
        logger.debug("removing local interactive container")
        container_cleanup = Popen(self.int_container.cleanup(), stdout=PIPE, stderr=PIPE)
        for line in iter(container_cleanup.stdout.readline, ''):
            logger.info(line)
        for line in iter(container_cleanup.stderr.readline, ''):
            logger.error(line)

        logger.debug("stopping and removing remote containers")
        for container in self.containers:
            if container.execution_host is not None:
                logger.debug('Removing container: ' + container.name + " On " + container.execution_host)
                command = ' '.join(container.terminate()) + " && " + ' '.join(container.cleanup())
                execute(self.execute_remote, command, host=container.execution_host)

        # Remove docker network if one was created
        if self.create_net:
            host_file_format = os.environ.get("DGRID_HOSTFILE_FORMAT")
            logger.debug("Removing docker network " + self.network_name)
            self.docker_network(create=False, remove=True)
            if host_file_format == 'json':
                os.remove(self.work_dir + "/hostfile.json")
            if host_file_format == 'list':
                os.remove(self.work_dir + "/hostfile")

    def remove_images(self):
        unref_command = ['sh', self.script_dir + settings.unreferenced_containers_script]

        if settings.image_cleanup == 1:
            logger.debug("Removing all unused images")
            base_command = ['sh', self.script_dir + settings.unused_images_script]
            commands = []

            if settings.remove_unreferenced_containers:
                commands.append(unref_command)
                commands.append(base_command)
            else:
                commands.append(base_command)

            for command in commands:
                image_cleanup = Popen(command, stdout=PIPE, stderr=PIPE)
                for line in iter(image_cleanup.stdout.readline, ''):
                    logger.info(line)
                for line in iter(image_cleanup.stderr.readline, ''):
                    logger.error(line)

            for container in self.containers:
                if container.execution_host is not None and settings.remove_unreferenced_containers:
                    execute(self.execute_remote, " ".join(unref_command), host=container.execution_host)
                    execute(self.execute_remote, " ".join(base_command), host=container.execution_host)
                if container.execution_host is not None and not settings.remove_unreferenced_containers:
                    execute(self.execute_remote, " ".join(base_command), host=container.execution_host)

        if settings.image_cleanup == 2:
            logger.debug("Removing images associated with job")
            for container in self.containers:
                if container.execution_host is not None and settings.remove_unreferenced_containers:
                    execute(self.execute_remote, ' '.join(unref_command), host=container.execution_host)
                    execute(self.execute_remote, ' '.join(container.image_cleanup), host=container.execution_host)
                if container.execution_host is not None and not settings.remove_unreferenced_containers:
                    execute(self.execute_remote, ' '.join(container.image_cleanup), host=container.execution_host)

            commands = []
            if settings.remove_unreferenced_containers:
                commands.append(unref_command)
                commands.append(self.int_container.image_cleanup)
            else:
                commands.append(self.int_container.image_cleanup)

            for command in commands:
                image_cleanup = Popen(command, stdout=PIPE, stderr=PIPE)
                for line in iter(image_cleanup.stdout.readline, ''):
                    logger.info(line)
                for line in iter(image_cleanup.stderr.readline, ''):
                    logger.error(line)

    def execute_remote(self, command):
        """
        Task that executes a given command on remote host
        :param command: Command to execute
        :return: Null
        """
        env.warn_only = True
        run(command.decode('utf-8'))
        env.warn_only = False

    def checkpoint_containers(self):
        pass

    def restore(self):
        pass
