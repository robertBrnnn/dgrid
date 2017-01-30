FROM python:2.7

ARG USER
ARG UID

RUN apt-get update && apt-get install -y openssh-server

RUN pip install pymongo fabric

RUN mkdir /var/run/sshd

RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's|UsePrivilegeSeparation|#UsePrivilegeSeparation|g' /etc/ssh/sshd_config
RUN printf "\nUsePrivilegeSeparation no" >> /etc/ssh/sshd_config

RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
ENV NOTVISIBLE "in users profile" \
    HOME=/home/${USER}

RUN echo "export VISIBLE=now" >> /etc/profile

RUN adduser --disabled-password --uid ${UID} --gecos "" ${USER} && \
    echo "${USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
    
ENV SSHDIR ${HOME}/.ssh/

RUN mkdir -p ${SSHDIR}

ADD ssh/config ${SSHDIR}/config
ADD ssh/id_rsa.mpi ${SSHDIR}/id_rsa
ADD ssh/id_rsa.mpi.pub ${SSHDIR}/id_rsa.pub
ADD ssh/id_rsa.mpi.pub ${SSHDIR}/authorized_keys

RUN chmod -R 600 ${SSHDIR}* && \
    chown -R ${USER}:${USER} ${SSHDIR} && \
    chown -R ${USER}:${USER} /etc/ssh && \
    chown -R ${USER}:${USER} /usr/local/lib/python2.7
    
RUN sed -i 's|Port 22|Port 2222|g' /etc/ssh/sshd_config
USER ${USER}
RUN chmod 600 ${SSHDIR}/*

EXPOSE 2222

CMD ["/usr/sbin/sshd", "-D"]
