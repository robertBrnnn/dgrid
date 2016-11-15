import os
import unittest
import socket
import threading
import time

from fabric.api import env
from fabric.tasks import execute
from dgrid.scheduling import schedule
from dgrid.scheduling.utils import fileparser
from dgrid.scheduling.utils.Errors import InteractiveContainerNotSpecified, HostValueError
from dgrid.scheduling.schedulers.Torque6.SSHExecutor import SSHExecutor

from dgrid.conf import settings


class SchedulerTester(unittest.TestCase):

    def setUp(self):
        # Generate the host file so that it contains current hostname
        self.host_template = "host1\nhost2\nhost3\n"
        # Set job ID to avoid errors
        os.environ['PBS_JOB_ID'] = '8'
        self.cwd = os.getcwd()
        self.host_template += socket.gethostname()
        self.hosts = self.cwd + '/tests/scheduling/generatedHF'
        self.cont = self.cwd + '/tests/scheduling/dockerdef1.json'
        env.user = 'root'
        env.password = 'dgridtest'
        env.reject_unknown_hosts = False
        env.disable_known_hosts = True

    def test_get_scheduler(self):
        with open(self.hosts, 'w') as f:
            f.write(self.host_template)

        scheduler = schedule.load_job(self.hosts, self.cont)
        assert scheduler.__class__.__name__ == settings.scheduler

    def test_get_scheduler1(self):
        containers = fileparser.get_containers(self.cont)
        hosts = fileparser.get_hosts(self.hosts)

        scheduler = schedule.Scheduler.get_scheduler(hosts, containers)
        assert scheduler.__class__.__name__ == settings.scheduler

    def test_get_scheduler_w_bad_container_def(self):
        containers = fileparser.get_containers(self.cwd + '/tests/scheduling/dockerdef2.json')
        hosts = fileparser.get_hosts(self.hosts)

        self.assertRaises(InteractiveContainerNotSpecified, schedule.Scheduler.get_scheduler, hosts, containers)

    def test_get_scheduler_wo_hostname(self):
        hosts = fileparser.get_hosts(self.hosts)
        containers = fileparser.get_containers(self.cont)

        hosts.remove(socket.gethostname())

        self.assertRaises(HostValueError, schedule.Scheduler.get_scheduler, hosts, containers)

    def test_running_remote_containers(self):
        # Spin up a couple of containers
        os.system('cd ' + self.cwd + '/TestingUtilities/ && docker build --build-arg HOM=$HOME -t dgrid:test .')

        for i in range(3):
            os.system('docker run -d -v /var/run/docker.sock:/run/docker.sock'
                      ' -p 900' + str(i) + ':22 dgrid:test')

        # create hostfile
        hostname = socket.gethostname()
        hosts = [hostname + ':9000', hostname + ':9001', hostname + ':9002', hostname]
        containers = fileparser.get_containers(self.cwd + '/tests/scheduling/Dockerdef3.json')

        executor = SSHExecutor(containers, hosts)
        execute(executor.run_container, containers[0], host=hosts[0])

        result = os.popen("docker ps | grep " + containers[0].name).read()
        assert len(result) > 0

    def test_running_local_container(self):
        hostname = socket.gethostname()
        hosts = [hostname + ':9000', hostname + ':9001', hostname + ':9002', hostname]
        containers = fileparser.get_containers(self.cwd + '/tests/scheduling/Dockerdef3.json')

        executor = SSHExecutor(containers, hosts)

        # executor.run_int_container()
        executor.run_int_container()
        result = os.popen("docker ps -a | grep " + executor.int_container.name).read()
        assert executor.local_pid > 0 and executor.int_container.name in result

    def tearDown(self):
        os.system("docker rm -fv $(docker ps -a | grep 'dgrid:test' | awk '{print $1}')")
        os.system("docker rm -fv $(docker ps -a | grep 'slave' | awk '{print $1}')")
        os.system("docker rm -fv $(docker ps -a | grep 'head' | awk '{print $1}')")
