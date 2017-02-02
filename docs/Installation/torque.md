# Torque specific installation

In settings.py the following properties are required:

1. cgroup_dir: full path to cgroups dir on nodes in the cluster
2. scheduler: this should be set to the scheduler class you need i.e Torque6
3. Execution_Method: the execution method to use i.e. SSH
4. termination_signal: Signal that DGrid should listen for to terminate a job 
   i.e. SIGHUP
5. pbs_track: the location of the pbs_track binary, 
   needed for Torque to monitor containers
6. enforce_memory_limits: on systems where Torque sets memory limits for jobs
   set to True, otherwise False
7. image_cleanup: the type of image_cleanup to run
8. remove_unreferenced_container: run container cleanup at end of execution, in case container left from previous jobs
9. paths to scripts: both unused_images_script and unreferenced_containers_script can be changed to custom scripts,
   place any custom scripts in the script directory before building DGrid.
   
The settings file can be modified after installation, by going to the dgrid/conf directory 
in your python packages directory. 
   
__Below is a Torque specific settings file__
   
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