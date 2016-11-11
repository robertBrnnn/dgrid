from setuptools import setup, find_packages

from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]


setup(
    name="DGrid",
    version="0.1-dev",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=reqs,
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
