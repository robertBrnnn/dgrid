from setuptools import setup, find_packages
from setuptools import Command
from pip.req import parse_requirements
import time
import os

exec(open('dgrid/version.py').read())
# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]

version = version_string


class VersionCommand(Command):
    user_options = [
        ('version=', 'v', 'major|minor|daily')
    ]
    description = 'update version'

    def initialize_options(self):
        self.version = None

    def finalize_options(self):
        if self.version is None:
            raise Exception("Parameter version is missing")
        print(self.version)

    def run(self):
        if self.version.lower() == 'major':

            version[0] = version[0] + 1
            print(".".join(str(x) for x in version))

            with open(os.getcwd() + "/dgrid/version.py", 'w+') as f:
                f.write("__version__ = '" + ".".join(str(x) for x in version) + "'\n")
                f.write("version_string = [" + ", ".join(str(x) for x in version) + "]\n")

        if self.version.lower() == 'minor':

            version[1] = version[1] + 1
            print(".".join(str(x) for x in version))

            with open(os.getcwd() + "/dgrid/version.py", 'w+') as f:
                f.write("__version__ = '" + ".".join(str(x) for x in version) + "'\n")
                f.write("version_string = [" + ", ".join(str(x) for x in version) + "]\n")

        if self.version.lower() == 'daily':

            print(".".join(str(x) for x in version))

            with open(os.getcwd() + "/dgrid/version.py", 'w+') as f:
                f.write("__version__ = '" + ".".join(str(x) for x in version) + "." + time.strftime("%d%m%Y") + "'\n")
                f.write("version_string = [" + ", ".join(str(x) for x in version) + "]\n")
            print("__version__ = '" + ".".join(str(x) for x in version) + "." + time.strftime("%d%m%Y") + "'\n")


setup(
    cmdclass={
              'uv': VersionCommand,
             },
    name="DGrid",
    version=__version__,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=reqs,
    data_files=[('/dgrid-scripts/', ['scripts/remove_unused.sh',
                                     'scripts/remove_unreferenced_containers.sh'])],
    package_data={
        '': ['*.md'],
    },
    entry_points={
          'console_scripts': [
              'dgrid = dgrid.__main__:main'
          ]
      },
    author="Robert J. Brennan",
    author_email="robert.brnnn@gmail.com",
    description="Batch task execution for Docker"
)
