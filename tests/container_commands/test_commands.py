import json
import unittest

from dgrid.docker.container import Container


class CommandTestSuite(unittest.TestCase):
    def setUp(self):
        containerdef1 = """
        {
          "interactive": "True",
          "image": "ubuntu:14.04",
          "name": "slave",
          "volumes": [
            "/var/www:/var/www",
            "/home/user:/home/user"],
          "work_dir": "/var/www",
          "checkpointing": "True",
          "run_cmd": [ "sh", "command.sh" ]
        }
        """
        data = json.loads(containerdef1)
        self.container = Container(data)

    def test_checkpoint_command(self):
        checkpoint_dir = "/tmp/checkpoint"
        checkpoint_name = "checkpoint1"
        self.container.checkpoint_dir = checkpoint_dir
        self.container.checkpoint_name = checkpoint_name
        expected_result = "docker checkpoint create --checkpoint-dir=%s %s %s" \
                          % (checkpoint_dir, self.container.name, checkpoint_name)
        print(' '.join(self.container.checkpoint()))
        assert ' '.join(self.container.checkpoint()) == expected_result

    def test_cleanup_command(self):
        expected_result = "docker rm -fv slave"
        assert ' '.join(self.container.cleanup()) == expected_result

    def test_termination_command(self):
        expected_result = "docker stop slave"

        assert ' '.join(self.container.terminate()) == expected_result

    def test_restore_command(self):
        checkpoint_dir = "/tmp/checkpoint"
        checkpoint_name = "checkpoint1"
        self.container.checkpoint_dir = checkpoint_dir
        self.container.checkpoint_name = checkpoint_name
        expected_result = "docker start --interactive=True --checkpoint-dir=%s --checkpoint=%s %s" \
                          % (checkpoint_dir, checkpoint_name, self.container.name)
        assert ' '.join(self.container.restore()) == expected_result

    def test_run_command1(self):
        expected_result = "docker run --interactive=True --detach=False" \
                          " -v /var/www:/var/www -v /home/user:/home/user --name=slave " \
                          "--workdir=/var/www ubuntu:14.04 sh command.sh"

        assert ' '.join(self.container.run()) == expected_result

    def test_run_command_w_cpusets(self):
        self.container.cpu_shares = '1024'
        self.container.cpu_set = '1'
        self.container.memory_swap = '30'
        self.container.memory = '444'
        self.container.memory_swappiness = '30'
        self.container.kernel_memory = '444'

        assert ' '.join(self.container.run()) == "docker run --interactive=True --detach=False" \
                                                 " --cpu-shares=1024 --cpuset-cpus=1" \
                                                 " --memory=444 --memory-swap=30 --memory-swappiness=30" \
                                                 " --kernel-memory=444 -v /var/www:/var/www -v /home/user:/home/user" \
                                                 " --name=slave --workdir=/var/www ubuntu:14.04 sh command.sh"

    def test_run_command2(self):
        containerdef2 = """
        {
          "interactive": "True",
          "image": "ubuntu:14.04",
          "name": "slave",
          "environment_variables": [
            "BINARY_HOME=/usr/bin",
            "RUN_TESTS=true"],
          "work_dir": "/var/www",
          "checkpointing": "True",
          "run_cmd": ["sh", "command.sh"]
        }
        """
        data = json.loads(containerdef2)
        self.container = Container(data)

        expected_result = "docker run --interactive=True --detach=False " \
                          "-e BINARY_HOME=/usr/bin -e RUN_TESTS=true --name=slave " \
                          "--workdir=/var/www ubuntu:14.04 sh command.sh"

        assert ' '.join(self.container.run()) == expected_result

    def test_run_command3(self):
        containerdef3 = """
        {
          "interactive": "True",
          "image": "ubuntu:14.04",
          "name": "slave",
          "work_dir": "/var/www",
          "checkpointing": "True",
          "run_cmd": ["sh", "command.sh"]
        }
        """

        data = json.loads(containerdef3)
        self.container = Container(data)

        expected_result = "docker run --interactive=True --detach=False" \
                          " --name=slave --workdir=/var/www ubuntu:14.04 sh command.sh"

        assert ' '.join(self.container.run()) == expected_result

    def test_run_command_detach(self):
        containerdef = """
        {
          "interactive": "False",
          "image": "ubuntu:14.04",
          "name": "slave",
          "environment_variables": [
            "BINARY_HOME=/usr/bin",
            "RUN_TESTS=true"],
          "work_dir": "/var/www",
          "checkpointing": "True",
          "run_cmd": ["sh", "command.sh"]
        }
        """

        data = json.loads(containerdef)
        self.container = Container(data)
        expected_result = "docker run --interactive=False --detach=True " \
                          "-e BINARY_HOME=/usr/bin -e RUN_TESTS=true --name=slave " \
                          "--workdir=/var/www ubuntu:14.04 sh command.sh"

        assert ' '.join(self.container.run()) == expected_result
