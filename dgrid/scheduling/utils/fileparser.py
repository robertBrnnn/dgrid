"""
Author: Robert Brennan
Email:  robert.brnnn@gmail.com

Utilities for parsing docker definition files and host file
"""

import json
import logging
import os

from dgrid.docker.container import Container

logger = logging.getLogger(__name__)


def get_containers(dockerdef):
    """
    Reads the json file, and returns an array of containers
    :param dockerdef: Json docker definition file
    :return: Container array
    """
    containers = []
    logger.debug('Loading container definition file')
    with open(dockerdef) as data_file:
        data = json.load(data_file)

    for cont in data["containers"]:
        # key error will be thrown if required values are missing from the json, no need to catch error
        if 'scale' in cont:
            for i in range(cont['scale']):
                containers.append(Container(cont))
        else:
            containers.append(Container(cont))

    if 'hostfile_format' in data:
        os.environ['DGRID_HOSTFILE_FORMAT'] = data["hostfile_format"]

    return containers


def get_hosts(hostfile=None):
    """
    Reads hostfile, and returns an array of hosts
    :param hostfile: File containing list of hosts assigned to job, split by '\n'
    :return: Hosts array
    """
    hosts = []
    if hostfile is None:
        logger.debug("No host file set")
        return None
    else:
        logger.debug('Loading host file')
        with open(hostfile, 'r') as f:
            host_list = f.read().splitlines()
            for host in host_list:
                hosts.append(host.decode('utf-8'))

        return hosts


def load_data(dockerdef, hostfile):
    """
    Calls get_containers(), and get_hosts(), returns both arrays generated from those methods
    :param dockerdef: Json docker definition file
    :param hostfile: '\n' seperated list of hosts assigned to job
    :return: Container array, Host array
    """
    return get_containers(dockerdef), get_hosts(hostfile)
