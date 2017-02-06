# Usage
On installation a command line utility is made available called dgrid.

For any job dgrid takes one parameter by default: 

1. --dockdef : the full path to the JSON file defining the containers to be run

There are four utility commands included as well:

1. --hostfile: the '\n' separated file of hosts assigned to the job by the scheduler
2. --version: displays the version of DGrid
3. --enable-debug: enables debug logging, to display more verbose output from DGrid
4. --help: displays the integrated of DGrid

__Notes on defining you JSON docker definition are available 
[here](../DockerDefinitions/docker_defs.md)__

__An example job for Torque can be found [here](../TorqueExample/torque_example.md)__
This example job explains some intricacies of Docker execution on Torque 
and how to overcome them.