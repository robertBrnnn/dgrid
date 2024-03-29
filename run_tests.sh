#!/bin/bash
# Author: Robert J. Brennan
# Runs the unitests for Dgrid
# Creates a dummy cgroups directory in users home directory on the host and in docker containers used for unit tests
# Dummy cgroups directory deleted after execution, and all containers are removed.

# NOTE: Ports 9000-9002 inclusive should be free, so as to run containers required for tests

echo 'Modifying settings files'
cp TestingUtilities/settings.py TestingUtilities/settings.py.bak
printf "\ncgroup_dir = \"$HOME/dgrid/cgroup\"" >> TestingUtilities/settings.py
printf "\npbs_track = \"$HOME/dgrid/pbs_track\"" >> TestingUtilities/settings.py

if [ ! -d "$HOME/dgrid" ]; then
  echo 'Creating dummy cgroups directory'
  mkdir -p $HOME/dgrid/cgroup/cpu/torque/8/ $HOME/dgrid/cgroup/cpuset/torque/8/ $HOME/dgrid/cgroup/memory/torque/8/ && \
    echo '1024' >> $HOME/dgrid/cgroup/cpu/torque/8/cpu.shares && \
    echo '1' >> $HOME/dgrid/cgroup/cpuset/torque/8/cpuset.cpus && \
    echo '524288000' >> $HOME/dgrid/cgroup/memory/torque/8/memory.limit_in_bytes && \
    echo '30' >> $HOME/dgrid/cgroup/memory/torque/8/memory.swappiness && \
    echo '524288000' >> $HOME/dgrid/cgroup/memory/torque/8/memory.memsw.limit_in_bytes && \
    echo '524288000' >> $HOME/dgrid/cgroup/memory/torque/8/memory.kmem.limit_in_bytes;

  printf "#!/bin/bash\nsleep 5" >> $HOME/dgrid/pbs_track
  chmod +x $HOME/dgrid/pbs_track
fi

mv dgrid/conf/settings.py dgrid/conf/settings.py.bak
cp TestingUtilities/settings.py dgrid/conf/settings.py

arg=$1
cover="cover"
if [ "$arg" = "$cover" ]; then
  echo "Running with html coverage"
  nosetests --with-cover --cover-package=dgrid --cover-html
else
  echo "Running without html coverage"
  nosetests --with-cover --cover-package=dgrid
fi

echo 'Cleaning Up'
rm dgrid/conf/settings.py
mv dgrid/conf/settings.py.bak dgrid/conf/settings.py
rm -rf $HOME/dgrid
rm TestingUtilities/settings.py
mv TestingUtilities/settings.py.bak TestingUtilities/settings.py
