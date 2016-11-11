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

        self.interactive = json['interactive']

        if 'work_dir' in json:
            self.work_dir = json['work_dir']

        self.memory = None
        self.cpu_shares = None
        self.cpu_set = None
        self.memory_swap = None
        self.memory_swappiness = None
        self.kernel_memory = None
        self.checkpointing = json['checkpointing']
        self.run_command = ['docker', 'run']
        self.chk_command = ['docker', 'checkpoint']
        self.rst_command = ['docker', 'restore']
        self.cln_command = ['docker', 'rm', '-fv']

    def run(self):
        """
        Builds the command to execute docker container
        :return: Command string for running container
        """
        self.add_argument('interactive', '--interactive')
        self.add_argument('cgroup_parent', '--cgroup-parent')
        self.add_argument('cpu_shares', '--cpu-shares')
        self.add_argument('cpu_set', '--cpuset-cpus')
        self.add_argument('memory', '--memory')
        self.add_argument('memory_swap', '--memory-swap')
        self.add_argument('memory_swappiness', '--memory-swappiness')
        self.add_argument('kernel_memory', '--kernel-memory')

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
        self.add_argument('cmd')

        return self.run_command

    def checkpoint(self):
        self.chk_command.append(self.name)
        return self.chk_command

    def restore(self):
        self.rst_command.append(self.name)
        return self.rst_command

    def cleanup(self):
        self.cln_command.append(self.name)
        return self.cln_command

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

    def add_param(self, param, vol=False, env=False):
        """
        Adds volumes or environment variables to the run command
        :param param: the value to be assigned as environment variable or or volume mapping
        :param vol: Checks if the parameter is a volume
        :param env: checks if the volume is an environment variable
        :return: Null
        """
        if vol:
            self.run_command.append('-v ' + param)
        if env:
            self.run_command.append('-e ' + param)