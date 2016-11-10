import unittest
import os

from scheduling import schedule
from conf import settings
from scheduling.utils import fileparser


class SchedulerTester(unittest.TestCase):

    def setUp(self):
        os.environ['PBS_JOB_ID'] = '8'
        self.cwd = os.getcwd()
        self.hosts = self.cwd + '/tests/scheduling/hostfile'
        self.cont = self.cwd + '/tests/scheduling/dockerdef1.json'

    def test_get_scheduler(self):
        scheduler = schedule.load_job(self.hosts, self.cont)
        assert scheduler.__class__.__name__ == getattr(settings, 'scheduler')

    def test_get_scheduler1(self):
        containers = fileparser.get_containers(self.cont)
        hosts = fileparser.get_hosts(self.hosts)

        scheduler = schedule.Scheduler.get_scheduler(hosts, containers)
        assert scheduler.__class__.__name__ == getattr(settings, 'scheduler')
