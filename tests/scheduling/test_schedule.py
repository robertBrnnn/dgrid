import unittest
import os

from scheduling import schedule


class SchedulerTester(unittest.TestCase):

    def test_is_torque6(self):
        scheduler_string = "torque6"
        # Don't need to pass containers or hosts, just checking correct class is instantiated
        sched = schedule.Scheduler.get_scheduler(scheduler_string, [], [])
        assert sched.__class__.__name__ == "Torque6"

    def test_get_full_scheduler(self):
        cwd = os.getcwd()
        hosts = cwd + '/tests/scheduling/hostfile'
        cont = cwd + '/tests/scheduling/dockerdef1.json'

        scheduler = schedule.load_job(hosts, cont, 'torque6')
        assert scheduler.__class__.__name__ == "Torque6"
