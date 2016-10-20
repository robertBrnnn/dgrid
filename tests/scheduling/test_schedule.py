import unittest
import os

from scheduling import schedule


class SchedulerTester(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        self.hosts = self.cwd + '/tests/scheduling/hostfile'
        self.cont = self.cwd + '/tests/scheduling/dockerdef1.json'
        self.mapping = self.cwd + "/scheduling/schedulers/mapping.py"

    def test_get_full_scheduler(self):
        schedulers = self.get_all_schedulers()
        for key in schedulers:
            scheduler = schedule.load_job(self.hosts, self.cont, key)
            assert scheduler.__class__.__name__ == schedulers[key]

    def get_all_schedulers(self):
        scheds = dict()
        with open(self.mapping, 'r') as f:
            # strip out blank lines
            lines = (line.rstrip() for line in f)
            lines = (line for line in lines if line)
            for line in lines:
                if line.startswith('#'):
                    continue
                else:
                    parts = line.split('=')
                    scheds[parts[0].replace(' ', '')] = parts[1].replace(' ', '').replace("'", "")
        return scheds
