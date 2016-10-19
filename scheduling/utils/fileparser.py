"""
Author: Robert Brennan
Email:  robert.brnnn@gmail.com

Utilities for parsing docker definition files and host file
"""

import json
from docker.container import Container


def get_containers(dockerdef):
    containers = []

    with open(dockerdef) as data_file:
        data = json.load(data_file)

    for cont in data["containers"]:
        # key error will be thrown if required values are missing from the json, no need to catch error
        containers.append(Container(cont))
    return containers


def get_hosts(hostfile):
    hosts = []

    with open(hostfile, 'r') as f:
        host_list = f.read().splitlines()
        for host in host_list:
            hosts.append(host)

    return hosts


def load_data(dockerdef, hostfile):
    return get_containers(dockerdef), get_hosts(hostfile)
