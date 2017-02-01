# Adding Scheduler Support

1. [Class naming convention](#class-naming-convention)
2. [Extending scheduler basse class](#scheduler-base-class)
3. [Container execution](#notes-on-container-execution)
4. [Custom shell scripts](#custom-shell-scripts)
5. [Documenting code](#documenting-code)
6. [Unit tests](#unit-tests)
7. [Schedulers with multiple execution methods](#schedulers-with-multiple-execution-methods)


##Class naming convention 

Say we want to add support for the scheduler "Awesome Scheduler". 
A new folder called AwesomeScheduler will be created at dgrid/scheduling/schedulers/AwesomeScheduler.
The name of the class file will be 'AwesomScheduler.py'.
The class defintion, implementing the scheduler base class will be called AwesomeScheduler.

DGrid is designed this way to make the loading of schedulers as simple as possible, with the addition of more schedulers.

##Scheduler Base Class

The scheduler base class is located in 'dgrid/scheduling/schedule.py' and is called Scheduler.
The Scheduler class is implemented as an abstract base class, all deriving classes must implement the functions listed in the class.

The static method get_scheduler in the Scheduler class will return the scheduler by the name defined in 'conf/settings.py'.
Schduer classes are retrieved by looking for 'dgrid/scheduling/schedulers/(scheduler_name)/(scheduler_name).py' as demonstrated above in Class naming convention.

__Class Parameters__

The scheduler class takes two parameters: Containers and hosts.
1. Containers is a list of container objects to be run by the job
2. Hosts is a list of hosts assigned to the job

##Notes on container execution

As each scheduler will have designs in how jobs are created, executed, and resourcs assigned, 
the execution of containers is managed entirely by the new scheduler classes, there are no assumptions made by DGrid.

DGrid provides custom errors for use in container execution, in 'dgrid/scheduling/utils/Errors.py'.
For networking, DGrid provides the function add_networking in 'dgrid/scheduling/utils/docker_networking.py'. 

~~TODO~~ Add documentation on docker_networking function. Add docs on logging setup.

##Custom shell scripts

To add custom shell scripts to DGrid for your scheduler class, you must:
1. add the shell scripts to the scripts directory.
2. add the script names to setup.py's data_files parameter so that they're included on a build

##Documenting code

~~TODO~~ Fill this in

##Unit tests

~~TODO~~ Fill this in

##Schedulers with multiple execution methods

In the case where a scheduler has different ways to execute a job, you should create seperate executor classes for each 
method and instantiate the executor in the schedulers init method. The execution method should be added as a parameter to 
'dgrid/conf/settings.py'
