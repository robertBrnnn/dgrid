# Copied from Docker image tutum/mongodb, https://github.com/tutumcloud/tutum-docker-mongodb
# Creates a mongodb image that should run on a Torque cluster job with DGrid

FROM ubuntu:14.04

ARG UID
ARG USER

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10 && \
    echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.0.list && \
    apt-get update && \
    apt-get install -y pwgen mongodb-org mongodb-org-server mongodb-org-shell mongodb-org-mongos mongodb-org-tools && \
    echo "mongodb-org hold" | dpkg --set-selections && echo "mongodb-org-server hold" | dpkg --set-selections && \
    echo "mongodb-org-shell hold" | dpkg --set-selections && \
    echo "mongodb-org-mongos hold" | dpkg --set-selections && \
    echo "mongodb-org-tools hold" | dpkg --set-selections
    
RUN adduser --disabled-password --uid ${UID} --gecos "" ${USER} && \
    echo "${USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    usermod -a -G mongodb $USER

# Can't use volumes as owner is root on host system (Look into alternatives in future)
# VOLUME /data/db

RUN mkdir -p /data/db
ENV AUTH yes
ENV STORAGE_ENGINE wiredTiger
ENV JOURNALING yes

ADD run.sh /run.sh
ADD set_mongodb_password.sh /set_mongodb_password.sh

RUN chown ${USER}:${USER} /run.sh /set_mongodb_password.sh && \
    chown -R `id -u $USER` /data/db && \
    chown -R `id -u $USER` /dev/null

EXPOSE 27017 28017

USER $USER

CMD ["/run.sh"]
