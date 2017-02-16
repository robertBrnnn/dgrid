import os
import unittest
import socket
import shutil

from dgrid.scheduling import schedule
from dgrid.scheduling.utils import fileparser
from dgrid.scheduling.utils.Errors import InteractiveContainerNotSpecified, HostValueError, ImportedSchedulerClassError

from dgrid.conf import settings


class SchedulerTester(unittest.TestCase):

    def setUp(self):
        # Generate the host file so that it contains current hostname
        self.host_template = "host1\nhost2\nhost3\n"
        self.cwd = os.getcwd()
        # Set job ID to avoid errors
        os.environ['PBS_JOBID'] = '8'
        os.environ['PBS_O_WORKDIR'] = self.cwd
        self.hostname = socket.gethostname()
        self.host_template += socket.gethostname()
        self.hosts = self.cwd + '/tests/scheduling/generatedHF'
        self.cont = self.cwd + '/tests/scheduling/dockerdef1.json'

    def test_01_get_scheduler(self):
        with open(self.hosts, 'w') as f:
            f.write(self.host_template)

        scheduler = schedule.load_job(self.cont, self.hosts)
        assert scheduler.__class__.__name__ == settings.scheduler

    def test_02_get_scheduler1(self):
        containers = fileparser.get_containers(self.cont)
        hosts = fileparser.get_hosts(self.hosts)

        scheduler = schedule.Scheduler.get_scheduler(containers, hosts)
        assert scheduler.__class__.__name__ == settings.scheduler

    def test_03_get_scheduler_w_bad_container_def(self):
        containers = fileparser.get_containers(self.cwd + '/tests/scheduling/dockerdef2.json')
        hosts = fileparser.get_hosts(self.hosts)

        self.assertRaises(InteractiveContainerNotSpecified, schedule.Scheduler.get_scheduler, containers, hosts)

    def test_04_get_scheduler_wo_hostname(self):
        hosts = fileparser.get_hosts(self.hosts)
        containers = fileparser.get_containers(self.cont)

        hosts.remove(socket.gethostname())

        self.assertRaises(HostValueError, schedule.Scheduler.get_scheduler, containers, hosts)

    def test_05_get_scheduler_not_implementing_scheduler_class(self):
        # Test whether get_scheduler will raise an error, over classes not implementing Scheduler base class
        containers = fileparser.get_containers(self.cont)
        # Create fake scheduler directory
        os.makedirs(self.cwd + '/dgrid/scheduling/schedulers/Test/')
        # Copy over fake scheduler
        shutil.copyfile(self.cwd + '/tests/scheduling/Test.py', self.cwd + '/dgrid/scheduling/schedulers/Test/Test.py')
        # Write empty __init__ file so python checks directory
        open(self.cwd + '/dgrid/scheduling/schedulers/Test/__init__.py', 'a').close()
        # Set schedule class setting value for scheduler to our new one
        setattr(schedule.settings, 'scheduler', 'Test')
        self.assertRaises(ImportedSchedulerClassError, schedule.Scheduler.get_scheduler, containers)

    def test_06_get_nonexistent_scheduler(self):
        containers = fileparser.get_containers(self.cont)
        setattr(schedule.settings, 'scheduler', 'DoesntExist')
        self.assertRaises(SystemExit, schedule.Scheduler.get_scheduler, containers)

    def tearDown(self):

        if os.path.isdir(self.cwd + '/dgrid/scheduling/schedulers/Test/'):
            shutil.rmtree(self.cwd + '/dgrid/scheduling/schedulers/Test/')
