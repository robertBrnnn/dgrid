# Usage
On installation a command line utility is made available called dgrid.

For any job dgrid takes two parameters by default: 

1. --dockdef : the full path to the JSON file defining the containers to be run
2. --hostfile: the '\n' separated file of hosts assigned to the job by the scheduler

There are three utility commands included as well:

1. --version: displays the version of DGrid
2. --enable-debug: enables debug logging, to display more verbose output from DGrid
3. --help: displays the integrated of DGrid

__Notes on defining you JSON docker definition are available 
[here](../DockerDefinitions/docker_defs.md)__