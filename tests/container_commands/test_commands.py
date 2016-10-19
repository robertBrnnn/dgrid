from docker.container import Container
import unittest
import json


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
          "run_cmd": "sh command.sh"
        }
        """
        data = json.loads(containerdef1)
        self.container = Container(data)

    def test_checkpoint_command(self):
        expected_result = "docker checkpoint slave"
        assert ' '.join(self.container.checkpoint()) == expected_result

    def test_cleanup_command(self):
        expected_result = "docker rm -fv slave"
        assert ' '.join(self.container.cleanup()) == expected_result

    def test_restore_command(self):
        expected_result = "docker restore slave"
        assert ' '.join(self.container.restore()) == expected_result

    def test_run_command1(self):
        expected_result = "docker run --interactive=True -v /var/www:/var/www -v /home/user:/home/user --name=slave " \
                          "--workdir=/var/www ubuntu:14.04 sh command.sh"

        assert ' '.join(self.container.run()) == expected_result

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
          "run_cmd": "sh command.sh"
        }
        """
        data = json.loads(containerdef2)
        self.container = Container(data)

        expected_result = "docker run --interactive=True -e BINARY_HOME=/usr/bin -e RUN_TESTS=true --name=slave " \
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
          "run_cmd": "sh command.sh"
        }
        """

        data = json.loads(containerdef3)
        self.container = Container(data)

        expected_result = "docker run --interactive=True --name=slave --workdir=/var/www ubuntu:14.04 sh command.sh"

        assert ' '.join(self.container.run()) == expected_result
