import os
import unittest

from dgrid.scheduling.utils import fileparser


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

    def test_creates_json_env(self):
        docker_def = self.cwd + '/tests/file_parser/dockerdef2.json'
        fileparser.get_containers(docker_def)

        file_format = os.environ.get('DGRID_HOSTFILE_FORMAT')

        assert file_format == 'json'

    def test_creates_list_env(self):
        docker_def = self.cwd + '/tests/file_parser/dockerdef3.json'
        fileparser.get_containers(docker_def)

        file_format = os.environ.get('DGRID_HOSTFILE_FORMAT')

        assert file_format == 'list'

    def test_bad_json(self):
        docker_def = self.cwd + '/tests/file_parser/bad_formatting.json'

        self.assertRaises(ValueError, fileparser.get_containers, docker_def)

    def test_no_json(self):
        self.assertRaises(IOError, fileparser.get_containers, self.cwd + '/tests/file_parser/DOES_NOT_EXIST.json')
