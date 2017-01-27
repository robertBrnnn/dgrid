import os
import unittest
import json
from dgrid.scheduling.utils import fileparser
from dgrid.scheduling.utils.docker_netorking import add_networking


class TestDockerNetworking(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        self.write_dir = self.cwd + '/tests/docker_networking/'
        self.docker_def_json = self.write_dir + 'def_json.json'
        self.docker_def_list = self.write_dir + 'def_list.json'
        self.docker_def_envs = self.write_dir + 'def_envs.json'

    def test_check_list_volumes(self):
        containers = fileparser.get_containers(self.docker_def_list)
        conts, var = add_networking(containers, self.write_dir)
        os.system("rm " + self.write_dir + "hostfile")
        for container in conts:
            if 'head' in container.name:
                result = self.run_check(container.volumes, islist=True)
                assert result is True and len(container.volumes) == 2 and var is True

    def test_check_json_volumes(self):
        containers = fileparser.get_containers(self.docker_def_json)
        conts, var = add_networking(containers, self.write_dir)
        os.system("rm " + self.write_dir + "hostfile.json")
        for container in conts:
            if 'head' in container.name:
                result = self.run_check(container.volumes, isjson=True)
                assert result is True and len(container.volumes) == 2 and var is True

    def test_check_json(self):
        containers = fileparser.get_containers(self.docker_def_json)
        add_networking(containers, self.write_dir)

        with open(self.write_dir + 'hostfile.json', 'r') as f:
            data = json.load(f)

        passes = []
        for val in data['green']:
            passes.append(True) if val.startswith("green") else passes.append(False)

        for val in data['red']:
            passes.append(True) if val.startswith("red") else passes.append(False)

        # Checks that all values are true, and length is correct
        assert all(item is True for item in passes) and len(data['red']) == 1 and len(data['green']) == 2

    def test_check_links(self):
        containers = fileparser.get_containers(self.docker_def_envs)
        conts, var = add_networking(containers, self.write_dir)

        for container in conts:
            if 'tail' in container.name:
                tail = container.name

        for container in conts:
            if 'head' in container.name:
                result = self.check_envs(container.environment_vars, tail)
                assert result is True and len(container.environment_vars) == 2 and var is True

    def test_check_list(self):
        containers = fileparser.get_containers(self.docker_def_list)
        conts, var = add_networking(containers, self.write_dir)

        expected = []
        for container in conts:
            if container.name.startswith('tail'):
                expected.append(container.name)

        with open(self.write_dir + 'hostfile', 'r') as f:
            lines = f.readlines()

        results = []
        for line in lines:
            line = line.replace("\n", "")
            results.append(True) if line in expected else results.append(False)

        # Check all results are true, and same number of entries in expected as result
        assert all(item is True for item in results) and len(expected) == len(results)

    def run_check(self, volumes, islist=False, isjson=False):
        result = False
        for volume in volumes:
            parts = volume.split(':')
            parts[0] = parts[0].replace('//', '/')

            if islist:
                result = True if self.write_dir + 'hostfile' in parts[0] else False
            if isjson:
                result = True if self.write_dir + 'hostfile.json' in parts[0] else False
        return result

    def check_envs(self, envs, slave):
        result = False
        for env in envs:
            parts = env.split('=')
            result = True if parts[0] == 'CONT' and parts[1] == slave else False
        return result

    def tearDown(self):
        # remove created hostfiles
        os.system("rm " + self.write_dir + "hostfile*")
