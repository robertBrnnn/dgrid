"""
Author: Robert Brennan
Email:  robert.brnnn@gmail.com

Class defining docker containers and their relevant commands
"""


class Container(object):

    def __init__(self, image, volumes, cgroupparent, name, run_cmd,
                 interactive, work_dir, memory, cpu_shares, cpu_set):
        self.image = image
        self.cgroup_parent = cgroupparent
        self.volumes = volumes
        self.name = name
        self.cmd = run_cmd
        self.interactive = interactive
        self.work_dir = work_dir
        self.memory = memory
        self.cpu_shares = cpu_shares
        self.cpu_set = cpu_set
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
        self.add_argument('cpu_set', '--cpu-set')
        self.add_argument('memory', '--memory')
        self.add_argument('name', '--name')
        self.add_argument('work_dir', '--workdir')
        self.add_argument('image')
        self.add_argument('cmd')

        for volume in self.volumes:
            self.add_volume(volume)

        return self.run_command

    def checkpoint(self):
        return self.chk_command.append(self.name)

    def restore(self):
        return self.rst_command.append(self.name)

    def cleanup(self):
        return self.cln_command.append(self.name)

    def add_argument(self, name, suffix=None):
        """
        Adds arguments to the run command
        :param name: Name of the parameter containing value to append to command
        :param suffix: Suffix to use for command parameter when required
        :return: Null
        """
        if suffix is None:
            if hasattr(self, name):
                self.run_command.append(getattr(self, name))
        else:
            if hasattr(self, name):
                self.run_command.append(suffix + "=" + getattr(self, name))

    def add_volume(self, volume):
        self.run_command.append('-v' + volume)
