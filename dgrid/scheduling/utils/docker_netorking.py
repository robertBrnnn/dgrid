"""
Author: Robert Brennan
Adds network logic to docker containers or use during execution
"""
import random
import string
import json
import os
import logging

logger = logging.getLogger(__name__)


def add_networking(containers, write_directory):
    """
    Reads container objects and modifies them to support docker multi-host networks
    :param containers: List of containers to add networking logic to
    :param write_directory: Directory to write host file to
    :return:
    """
    format_used = os.environ.get("DGRID_HOSTFILE_FORMAT")
    create_network = False
    container_mapping = dict()
    for container in containers:
        original_name = container.name
        container.name += ''.join([random.choice(string.ascii_lowercase + string.digits) for n in range(20)])
        container_mapping[original_name] = container.name

    for container in containers:
        if container.links is not None:
            create_network = True
            # add correct container name to environment variables
            for link in container.links:
                parts = link.split(":")
                # get new container name from mapping
                container_name = container_mapping[parts[0]]
                # get containers env variable list if it exist else empty list
                logger.debug("setting env variable %s to value %s" % (parts[1], container_name))
                environment_variables = container.environment_vars if hasattr(container, 'environment_vars') else []
                # append new environment variable with container name
                environment_variables.append("%s=%s" % (parts[1], container_name))
                # set container environment variables to new environment variable list
                container.environment_vars = environment_variables
                logger.debug("Container environment variables " + " ".join(container.environment_vars))
                logger.debug("Container run command " + " ".join(container.run()))

        if container.host_to_list is not None:
            create_network = True
            # add container host name to list
            if format_used == "json":
                htl = dict()
                for val in container.host_to_list:
                    parts = val.split("=")
                    htl[parts[0]] = parts[1]
                add_to_hostlist(container.name, write_directory, tag=htl['tag'], formatter=format_used)

            if format_used == "list":
                add_to_hostlist(container.name, write_directory, formatter=format_used)

        if container.host_list_location is not None:
            create_network = True
            # add volume mapping for host list
            if format_used == 'json':
                hostfile = write_directory + "/" + "hostfile.json"
                volumes = container.volumes if hasattr(container, 'volumes') else []
                volumes.append('%s:%s' % (hostfile, container.host_list_location + "hostfile.json"))
                container.volumes = volumes

            if format_used == 'list':
                hostfile = write_directory + "/" + "hostfile"
                volumes = container.volumes if hasattr(container, 'volumes') else []
                volumes.append('%s:%s' % (hostfile, container.host_list_location + "hostfile"))
                container.volumes = volumes

    return containers, create_network


def add_to_hostlist(name, write_directory, tag=None, formatter=None):
    """
    Adds container names to host list used by containers
    :param name: Hostname to write to file
    :param write_directory: directory to write file to
    :param tag: In the case of json, the list name to add host to
    :param formatter: Format for hostfile. i.e. list | json
    :return:
    """
    if formatter == "list":
        hf = "hostfile"
        with open(write_directory + '/' + hf, 'a+') as hf:
            hf.write(name + '\n')

    if formatter == "json":
        hf = "hostfile.json"
        json_writer(write_directory + '/' + hf, name, tag)


def json_writer(file, name, tag):
    """
    Adds host names to a json host list for use in docker containers
    :param file: Json file to write hosts to
    :param name: Hostname to add to file
    :param tag: List to add hostname to
    :return: Null
    """

    if not os.path.isfile(file):
        # Create the file, and entry
        data = '{"%s": ["%s"]}' % (tag, name)
        with open(file, 'w') as f:
            f.write(data)
    else:
        # Read the file
        with open(file, 'r') as f:
            data = json.load(f)

        if tag not in data:
            # if the tag doesn't exist create it and append to it
            data[tag] = []
            data[tag].append("%s" % name)
        else:
            # append to existing tag
            data[tag].append("%s" % name)

        with open(file, 'w') as f:
            # write the new data to the file overwriting the existing one
            json.dump(data, f)
