import os
import unittest
import socket

from dgrid.scheduling import schedule
from dgrid.scheduling.utils import fileparser
from dgrid.scheduling.utils.Errors import InteractiveContainerNotSpecified, HostValueError

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
