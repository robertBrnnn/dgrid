"""
Author: Robert Brennan
Email:  robert.brnnn@gmail.com

Class defining docker containers and their relevant commands
"""


class Container(object):

    def __init__(self, json):
        """
        Initializes a container object
        :param json: Json object of container to instantiate
        """
        self.image = json['image']
        self.cgroup_parent = None

        if 'volumes' in json:
            self.volumes = json['volumes']

        self.name = json['name']

        if 'run_cmd' in json:
            self.cmd = json['run_cmd']

        if 'environment_variables' in json:
            self.environment_vars = json['environment_variables']

        if json['interactive'] == 'True':
            self.interactive = 'True'
            self.detach = 'False'
        else:
            self.detach = 'True'
            self.interactive = 'False'

        if 'work_dir' in json:
            self.work_dir = json['work_dir']

        self.host_to_list = json['host_to_list'] if 'host_to_list' in json else None
        self.host_list_location = json['host_list_location'] if 'host_list_location' in json else None
        self.links = json['links'] if 'links' in json else None

        self.user = None
        self.network = None
        self.memory = None
        self.cpu_shares = None
        self.cpu_set = None
        self.memory_swap = None
        self.memory_swappiness = None
        self.kernel_memory = None
        self.checkpointing = json['checkpointing'] if 'checkpointing' in json else None
        self.run_command = None
        self.chk_command = None
        self.rst_command = None
        self.cln_command = None
        self.term_command = None
        self.image_cleanup = ['docker', 'rmi', self.image]
        # Save the assigned host with the container object
        self.execution_host = None

    def run(self):
        """
        Builds the command to execute docker container
        :return: Command string for running container
        """
        self.run_command = ['docker', 'run']

        # Add arguments to run command. Structure of docker run command must be adhered to.
        self.add_argument('interactive', '--interactive')
        self.add_argument('detach', '--detach')
        self.add_argument('cgroup_parent', '--cgroup-parent')
        self.add_argument('cpu_shares', '--cpu-shares')
        self.add_argument('cpu_set', '--cpuset-cpus')
        self.add_argument('memory', '--memory')
        self.add_argument('memory_swap', '--memory-swap')
        self.add_argument('memory_swappiness', '--memory-swappiness')
        self.add_argument('kernel_memory', '--kernel-memory')
        self.add_argument('user', '--user')
        self.add_argument('network', '--network')

        if hasattr(self, 'volumes'):
            for volume in self.volumes:
                # self.add_volume(volume)
                self.add_param(volume, vol=True)

        if hasattr(self, 'environment_vars'):
            for env_var in self.environment_vars:
                self.add_param(env_var, env=True)

        self.add_argument('name', '--name')
        self.add_argument('work_dir', '--workdir')
        self.add_argument('image')
        if hasattr(self, 'cmd'):
            for arg in self.cmd:
                self.add_param(arg, cmd=True)

        return self.run_command

    def checkpoint(self):
        """
        Builds checkpoint command
        :return: Command for Checkpointing container
        """
        self.chk_command = ['docker', 'checkpoint']
        self.chk_command.append(self.name)
        return self.chk_command

    def restore(self):
        """
        Builds docker restore command
        :return: Command for restoring container
        """
        self.rst_command = ['docker', 'restore']
        self.rst_command.append(self.name)
        return self.rst_command

    def cleanup(self):
        """
        Builds command for container removal
        :return: Command to remove the docker container, with force and volumes
        """
        self.cln_command = ['docker', 'rm', '-fv']
        self.cln_command.append(self.name)
        return self.cln_command

    def terminate(self):
        """
        Builds command for stopping running container
        :return: Command to stop running container
        """
        self.term_command = ['docker', 'stop']
        self.term_command.append(self.name)
        return self.term_command

    def add_argument(self, name, suffix=None):
        """
        Adds arguments to the run command
        :param name: Name of the parameter containing value to append to command
        :param suffix: Suffix to use for command parameter when required
        :return: Null
        """
        if suffix is None:
            if hasattr(self, name) and getattr(self, name) is not None:
                self.run_command.append(getattr(self, name))
        else:
            if hasattr(self, name) and getattr(self, name) is not None:
                self.run_command.append(suffix + "=" + getattr(self, name))

    def add_param(self, param, vol=False, env=False, cmd=False):
        """
        Adds volumes or environment variables to the run command
        :param param: the value to be assigned as environment variable or or volume mapping
        :param vol: Checks if the parameter is a volume
        :param env: checks if the volume is an environment variable
        :param cmd: Checks if the parameter is part of the run command
        :return: Null
        """
        if vol:
            self.run_command.append('-v')
            self.run_command.append(param)
        if env:
            self.run_command.append('-e')
            self.run_command.append(param)
        if cmd:
            self.run_command.append(param)
