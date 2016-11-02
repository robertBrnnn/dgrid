from scheduling.utils import fileparser
import unittest
import os


class FileParserTests(unittest.TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        self.docker_def_1 = self.cwd + '/tests/scheduling/dockerdef1.json'
        self.docker_def_scaled = self.cwd + '/tests/file_parser/dockerdef.json'

    def test_no_scaling(self):
        containers = fileparser.get_containers(self.docker_def_1)

        assert len(containers) == 2

    def test_with_scaling(self):
        containers = fileparser.get_containers(self.docker_def_scaled)

        assert len(containers) == 4
