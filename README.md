# DGrid - Docker Grid Project

## Overview

Dgrid is a utility that adds support for batch task execution with Docker to existing schedulers. 

When executing jobs with DGrid you can use as many Docker images as you need, run the containers in parallel, 
defining how each container will run, volume management, environment variables etc. You are entirely in control 
of your task and are not restricted by a schedulers implementation of Docker support.

Jobs are executed like an MPI task i.e. you still submit your job as normal, requesting resources from your cluster e.g. via a job submission script. 
However, to run your docker based task, you call the dgrid executable in the job submission script, passing it your Job Definition File 
(the file where you define your containers, and their requirements).

Jobs are defined in JSON format, and are submitted to DGrid for execution.

__usage instructions available [here](../master/docs/Usage/usage.md)__


## Installation

Dgrid must be built from source using python pip

Dgrid is installed as a .whl package using python pip

Full installation docs [here](../master/docs/Installation/installation.md)


## Scheduler Support

Torque 6 is the only supported scheduler currently.

Documentation on adding support for other schedulers can be found [here](../master/docs/Adding Scheduler Support/schedulers.md)


## Why create this?

Existing resource managers/schedulers for example, Torque, HTCondor, offer restricted use of Docker on their systems, such as 
a single image per task, or only one container per task. What if you have a task that requires a database, that can't be installed 
on your cluster, and require a specific python version for running analysis on that data? That's where DGrid comes in, with it 
you can run multiple images simultaneously, and with support for Docker overlay networks, all containers can communicate with each 
other. Just like MPI uses SSH, Docker images configured with shared ssh keys can run exactly the same through DGrid.

By using Docker for your computing tasks, and DGrid as the task runner on your cluster, you can ensure that the runtime environment 
is exactly the same in development as it is in production. So no more porting the development code for the production cluster, no longer 
having to remeber which modules to load/unload from your PATH before execution, just remember the Docker images, and their configuration. 


## Future

DGrid is inactive for now until I get my own hardware for replicating a small cluster locally, 
and I get time on my hands.

As for future goals: 

1. Supporting more schedulers probably HTCondor next

2. Adding support for Python 3 / Turning DGrid into an entirely Python 3 framework (we'll see)
