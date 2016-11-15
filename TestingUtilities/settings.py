# Import any signal needed
from signal import SIGTERM

DEBUG = True

# Scheduler type & version
scheduler = "Torque6"

# Execution method
Execution_Method = 'SSH'

# Termination signals
termination_signal = SIGTERM

'''
Image cleanup possibilities:
0) No removal of images. Must be carried out manually or automated job.
1) At the end of execution remove all unused images on nodes assigned to the job.
2) Remove only images associated with the job.
'''
# image_cleanup = 0
# image_cleanup = 1
image_cleanup = 2
