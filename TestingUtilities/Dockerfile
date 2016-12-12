# Inspired by https://docs.docker.com/engine/examples/running_ssh_service/
# Creates an image for mocking a torque grid with cgroups at a user defined location
FROM ubuntu:16.04

ARG HOM

RUN apt-get update && apt-get install -y openssh-server
RUN mkdir /var/run/sshd
RUN echo 'root:dgridtest' | chpasswd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

RUN mkdir -p $HOM/dgrid/cgroup/cpu/torque/8/ $HOM/dgrid/cgroup/cpuset/torque/8/ $HOM/dgrid/cgroup/memory/torque/8/ && \
    echo '1024' >> $HOM/dgrid/cgroup/cpu/torque/8/cpu.shares && \
    echo '1' >> $HOM/dgrid/cgroup/cpuset/torque/8/cpuset.cpus && \
    echo '524288000' >> $HOM/dgrid/cgroup/memory/torque/8/memory.limit_in_bytes && \
    echo '30' >> $HOM/dgrid/cgroup/memory/torque/8/memory.swappiness && \
    echo '524288000' >> $HOM/dgrid/cgroup/memory/torque/8/memory.memsw.limit_in_bytes && \
    echo '524288000' >> $HOM/dgrid/cgroup/memory/torque/8/memory.kmem.limit_in_bytes

RUN printf '#!/bin/bash\nsleep 5' >> $HOM/dgrid/pbs_track && chmod a+x $HOM/dgrid/pbs_track && \
    export PATH=$HOM/dgrid:$PATH

RUN apt-get install -y curl && \
    curl -L https://get.docker.com/builds/Linux/x86_64/docker-1.10.3 > /usr/bin/docker && \
    chmod +x /usr/bin/docker

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
