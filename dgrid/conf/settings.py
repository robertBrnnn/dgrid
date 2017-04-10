"""
    Copyright (C) 2017  Robert James Brennan
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# Import any signal needed
from signal import SIGTERM

# Enable debug log messages to stdout
DEBUG = False

'''
Scheduler configuration
'''
# Scheduler type & version
scheduler = "Torque6"

# Execution method
Execution_Method = 'SSH'

# Termination signals
termination_signal = SIGTERM

# pbs_track binary
pbs_track = "/usr/local/bin/pbs_track"

'''
Linux control group configuration.
cgroup_dir: the path to the machines cgroup directory
enforce_memory_limits: on systems where memory limits are enforced in cgroups, apply to spun up containers
'''
cgroup_dir = '/sys/fs/cgroup'
enforce_memory_limits = False

'''
Image cleanup possibilities:
0) No removal of images. Must be carried out manually or automated job.
1) At the end of execution remove all unused images on nodes assigned to the job.
2) Remove only images associated with the job.
'''
image_cleanup = 0
# image_cleanup = 1
# image_cleanup = 2

'''
Remove containers using unreferenced images
This will allow dangling images to be removed, when containers exist that use them.
'''
remove_unreferenced_containers = True

'''
Image cleanup script references

Note: Scripts are installed in Python's package directory in folder 'dgrid-scripts'.
      Users can create modified cleanup scripts, place them in the dgrid-scripts directory and reference them here.
'''
unused_images_script = "remove_unused.sh"
unreferenced_containers_script = "remove_unreferenced_containers.sh"
