# Import any signal needed
from signal import SIGTERM

DEBUG = True

# Scheduler type & version
scheduler = "Torque6"

# Execution method
Execution_Method = 'SSH'

# Termination signals
termination_signal = SIGTERM

# Cgroups directory of Torque
cgroup_dir = '/sys/fs/cgroup'

'''
Image cleanup possibilities:
0) No removal of images. Must be carried out manually or automated job.
1) At the end of execution remove all unused images on nodes assigned to the job.
2) Remove only images associated with the job.
'''
# image_cleanup = 0
image_cleanup = 1
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
