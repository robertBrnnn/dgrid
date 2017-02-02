# Docker Definition Files

__Defining containers__

In the JSON file you must create a containers 
element that takes a list of containers you wish to run in this job.

The required parameters for every container are:

1. interactive: the container from which logs are retrieved, 
   only one interactive container can be assigned to a job.
2. image: the docker image you wish to use
3. name: the name to assign to the container. 
   This gets appended with a random string before execution 
   to prevent naming conflicts on Docker daemons and networks

The optional parameters available are:

1. volumes: a list of "host:container" volume mappings, 
   these must always be full paths, no relative paths
2. environment_variables: a list of "variable=value" environment variable
   mappings, to inject into the containers run time shell
3. work_dir: the directory within the container that 
   the containers shell will spawn in at start up.
4. run_cmd: the command to run at startup of the container as a list
5. scale: the number of this container to spin up. 
   This can only be used with non interactive containers
6. checkpointing: whether the container should be 
   checkpointed given a termination signal to the job. 
   __NOTE__ support for checkpointing is not currently available.
   
Below is an example docker definition file to give some context:

    {
      "containers":[{
          "interactive": "True",
          "image": "ubuntu:14.04",
          "name": "head",
          "volumes": [
            "/var/www:/var/www",
            "/home/user:/home/user"],
          "work_dir": "/var/www",
          "checkpointing": "True",
          "run_cmd": ['sh', 'command.sh']
        },
        {
          "image": "ubuntu:14.04",
          "name": "slave",
          "interactive": "False",
          "volumes": [
            "/var/www:/var/www",
            "/home/user:/home/user"],
          "environment_variables": [
            "variable=value"
          ],
          "work_dir": "/var/www",
          "checkpointing": "False",
          "scale": 3,
          "run_cmd": ['sh', 'command.sh']
        }
      ]
    }
    
## Docker networking in docker definition files

To enable networking between containers, there are three options available:

1. [linked by environment variables](#linked-by-environment-variables)
2. [Json host list](#json-host-list)
3. ['\n' separated list of hosts](#typical-host-list)

### Linked by environment variables

    { "containers":[{
              "interactive": "True",
              "image": "ubuntu:14.04",
              "name": "head",
              "checkpointing": "True",
              "run_cmd": ["sh", "run.sh"],
              "links": ["tail:CONT"]
            },
            {
              "image": "ubuntu:14.04",
              "name": "tail",
              "interactive": "False",
              "checkpointing": "False",
              "run_cmd": ["sh", "run.sh"]
            }
        ]
    }

In the above definition, the container 'head' asks for an environment 
variable called 'CONT' to store the name of the container tail. 
This environment variable will be made available to the 'head' container at startup.
In the case of multiple links, just add the link mappings to the list.

The format for a link is: "original_name:environment_variable_name", 
where original_name is the name you assign to the container in your definition file,
and environment_variable_name is the environment variable to hold the containers assigned name.

__Note__ You cannot use links when the container you want to link to has a scale defined.
         You can only use links with containers that have no scale set, i.e. there will only be one of them
         
### Json host list

    {"hostfile_format": "json",
    "containers":[{
              "interactive": "True",
              "image": "python:2",
              "name": "head",
              "checkpointing": "True",
              "run_cmd": ["python", "script.py"],
              "host_list_location": "/"
            },
            {
              "image": "ubuntu:14.04",
              "name": "tail",
              "interactive": "False",
              "checkpointing": "False",
              "run_cmd": ["sh", "test.sh"],
              "scale": 2,
              "host_to_list": ["tag=green"]
            },
            {
              "image": "ubuntu:14.04",
              "name": "tail",
              "interactive": "False",
              "checkpointing": "False",
              "run_cmd": ["sh", "test.sh"],
              "host_to_list": ["tag=red"]
            }
        ]
    }

In the above definition, the new element "hostfile_format" is added, and set to json,
this tells DGrid the file format to create, this must always be defined for json host lists.

The interactive container, has an attribute host_list_location, this specifies where the file 
will be put inside the container for access during execution. Any containers that need the hostfile 
must have host_list_location defined.

Both definitions of non interactive containers have the attribute "host_to_list", this tells DGrid 
to write the containers name to the host list. The value of "host_to_list" must be a list defining
a tag to associate with that container type. The generated hostlist in the above case, will have a 
red list and a green list. This is useful where, one container may be a database, and the others 
workers.

### Typical host list

    {"hostfile_format": "list",
    "containers":[{
              "interactive": "True",
              "image": "python:2",
              "name": "head",
              "volumes": [
                "/home/u170606/dgrid-tests/nethl/net.py:/net.py"],
              "checkpointing": "True",
              "run_cmd": ["python", "/net.py"],
              "host_list_location": "/"
            },
            {
              "image": "ubuntu:14.04",
              "name": "tail",
              "interactive": "False",
              "volumes": [
                "/home/u170606/dgrid-tests/test1/test.sh:/test.sh"],
              "checkpointing": "False",
              "run_cmd": ["sh", "test.sh"],
              "scale": 3,
              "host_to_list": "True"
            }
        ]
    }

In the above definition, the new element "hostfile_format" is added, and set to list,
this tells DGrid the file format to create, this must always be defined for '\n' separated host lists.

The interactive container, has an attribute host_list_location, this specifies where the file 
will be put inside the container for access during execution. Any containers that need the hostfile 
must have host_list_location defined.

The tail container has the attribute "host_to_list", this tells DGrid to write the containers 
name to the host list. The value of "host_to_list", in this case should just be set to "True".
There is no way to differentiate hosts with '\n' separated lists, if this is what you need, use 
json host lists. 

'\n'  separated lists are useful for scenarios where it doesnt matter what type the container is.