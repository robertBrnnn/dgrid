from dgrid.scheduling.schedulers.Torque6.SSHExecutor import SSHExecutor
from dgrid.scheduling.utils import fileparser
from fabric.api import env
from fabric.tasks import execute

import os
import unittest
import socket


class SSHExecutorTests(unittest.TestCase):

    def setUp(self):
        env.user = 'root'
        env.password = 'dgridtest'
        env.reject_unknown_hosts = False
        env.disable_known_hosts = True
        # Generate the host file so that it contains current hostname
        self.host_template = "host1\nhost2\nhost3\n"
        # Set job ID to avoid errors
        os.environ['PBS_JOBID'] = '8'
        self.cwd = os.getcwd()
        self.hostname = socket.gethostname()
        self.host_template += socket.gethostname()

    def test_01_running_remote_containers(self):
        # Spin up a couple of containers
        os.system('cd ' + self.cwd + '/TestingUtilities/ && docker build --build-arg HOM=$HOME -t dgrid:test .')

        for i in range(3):
            os.system('docker run -d -v /var/run/docker.sock:/run/docker.sock'
                      ' -p 900' + str(i) + ':22 dgrid:test')

        # create hostfile
        hosts = [self.hostname + ':9000', self.hostname + ':9001', self.hostname + ':9002', self.hostname]
        containers = fileparser.get_containers(self.cwd + '/tests/torque/Dockerdef3.json')

        executor = SSHExecutor(containers, hosts)
        execute(executor.run_container, containers[0], host=hosts[0])

        # Check if container was run
        result = os.popen("docker ps | grep " + containers[0].name).read()

        # Clean up
        os.system("docker rm -fv $(docker ps -a | grep 'dgrid:test' | awk '{print $1}')")
        os.system("docker rm -fv $(docker ps -a | grep 'slave' | awk '{print $1}')")
        assert containers[0].name not in result

    def test_02_running_local_container(self):
        hosts = [self.hostname + ':9000', self.hostname + ':9001', self.hostname + ':9002', self.hostname]
        containers = fileparser.get_containers(self.cwd + '/tests/torque/Dockerdef3.json')

        executor = SSHExecutor(containers, hosts)

        # executor.run_int_container()
        executor.run_int_container()
        result = os.popen("docker ps -a | grep " + executor.int_container.name).read()

        # Clean Up
        os.system("docker rm -fv $(docker ps -a | grep 'head' | awk '{print $1}')")
        assert executor.local_pid > 0 and executor.int_container.name in result

    def test_03_removing_containers(self):
        for i in range(3):
            os.system('docker run -d -v /var/run/docker.sock:/run/docker.sock'
                      ' -p 900' + str(i) + ':22 dgrid:test')

        hosts = [self.hostname + ':9000', self.hostname + ':9001', self.hostname + ':9002', self.hostname]
        containers = fileparser.get_containers(self.cwd + '/tests/torque/Dockerdef3.json')

        executor = SSHExecutor(containers, hosts)

        print executor.containers

        for x in range(len(executor.containers)):
            container = executor.containers[x]

            execute(executor.run_container, container, host=hosts[x])
            container.execution_host = hosts[x]

        executor.terminate_clean()

        results = []
        for x in range(len(executor.containers)):
            results.append(executor.containers[x].name not in
                           os.popen("docker ps -a | grep " +
                                    executor.containers[x].name +
                                    " | awk '{print $1}'").read())
            #assert executor.containers[x].name not in \
            #       os.popen("docker ps -a | grep " + executor.containers[x].name + " | awk '{print $1}'").read()
        assert all(item is True for item in results)

    def tearDown(self):
        os.system("docker rm -fv $(docker ps -a | grep 'dgrid:test' | awk '{print $1}')")
