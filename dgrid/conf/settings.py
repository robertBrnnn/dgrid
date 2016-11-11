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
cgroup_dir = '/sys/fs/cgroup/'

# Image cleanup (If set to true, unused images will be deleted after job execution)
image_cleanup = True
