# Example Torque Job

## Sumission script

example.pbs

    #PBS -l nodes=4
    #PBS -l walltime=00:10:00
    
    dgrid --hostfile=$PBS_NODEFILE --dockdef=/FULL/PATH/TO/dockerdef.json


## Dockerfiles for job

### MongoDB

    # Copied from Docker image tutum/mongodb, https://github.com/tutumcloud/tutum-docker-mongodb
    # Creates a mongodb image that should run on a Torque cluster job with DGrid
    
    FROM ubuntu:14.04
    
    # Step 1
    ARG UID
    ARG USER
    
    # Step 2
    RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10 && \
        echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.0.list && \
        apt-get update && \
        apt-get install -y pwgen mongodb-org mongodb-org-server mongodb-org-shell mongodb-org-mongos mongodb-org-tools && \
        echo "mongodb-org hold" | dpkg --set-selections && echo "mongodb-org-server hold" | dpkg --set-selections && \
        echo "mongodb-org-shell hold" | dpkg --set-selections && \
        echo "mongodb-org-mongos hold" | dpkg --set-selections && \
        echo "mongodb-org-tools hold" | dpkg --set-selections
        
    # Step 3    
    RUN adduser --disabled-password --uid ${UID} --gecos "" ${USER} && \
        echo "${USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
        usermod -a -G mongodb $USER
    
    # Can't use volumes as owner is root on host system (Look into alternatives in future)
    # VOLUME /data/db
    
    RUN mkdir -p /data/db
    ENV AUTH yes
    ENV STORAGE_ENGINE wiredTiger
    ENV JOURNALING yes
    
    # Step 4
    ADD run.sh /run.sh
    ADD set_mongodb_password.sh /set_mongodb_password.sh
    
    # Step 5
    RUN chown ${USER}:${USER} /run.sh /set_mongodb_password.sh && \
        chown -R `id -u $USER` /data/db && \
        chown -R `id -u $USER` /dev/null
    
    # Step 6
    EXPOSE 27017 28017
    
    # Step 7
    USER $USER
    
    # Step 8
    CMD ["/run.sh"]
    
The above Dockerfile generates a MongoDB image. 
For Torque to be able to track a process (Docker container), 
the container cannot run as root, instead it must run as the submitter.
Therefore, any processes run within the container must be owned by the submitter
 and not the root user.
 
To build docker images for Torque, users should create images with their username and UID
on the cluster where the image will be run.

1. The above image has two build time arguments USER and UID, these are used to create
a user in the Docker image, with their UID and username set to the build time args.

2. Next MongoDB and all required software is installed.

3. On the adduser command we set UID to the build time argument UID, and username to 
build time argument USER. The user is then added to the mongodb group, so as to allow
execution of mongodb by that user.

4. Required files for execution added to the image

5. Added files have their ownership changed to that of the new user, and not root.

6. The ports used by mongodb are exposed.

7. The run time user is set to the newly created user.

8. Finally, the main command for runtime is set to the run.sh script.

__NOTE__ Volumes should not be created in Dockerfiles, as they will always be owned by
root, this will prevent execution by docker and tracking by Torque. Volumes should only
ever be defined in your docker definition submit script to DGrid.

To build the above image, use the Dockerfile in "docker_images/dgrid.mongodb", run the following command:
```docker build --build-arg UID=$(id -u $USER) --build-arg USER=$USER -t dgrid.mongodb .```

The scripts added to the docker image can be viewed from the "docker_images/dgrid.mongodb"
directory.
    
### PySSH

    FROM python:2.7
    
    # Step 1
    ARG USER1
    ARG UID1
    
    # Step 2
    RUN apt-get update && apt-get install -y openssh-server
    RUN pip install pymongo fabric retry
    RUN mkdir /var/run/sshd
    
    #Step 3
    RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config
    RUN sed -i 's|UsePrivilegeSeparation|#UsePrivilegeSeparation|g' /etc/ssh/sshd_config
    RUN printf "\nUsePrivilegeSeparation no" >> /etc/ssh/sshd_config
    RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
    
    # Step 4
    ENV NOTVISIBLE "in users profile" \
        HOME1=/home/$USER1
    
    # Step 5
    RUN echo "export VISIBLE=now" >> /etc/profile
    RUN useradd -m -d /home/$USER1 -u $UID1 $USER1 && \
        echo "$USER1:password" | chpasswd && \
        echo "$USER1 ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers 
    ENV SSHDIR $HOME1/.ssh/
    
    # Step 6
    RUN mkdir -p ${SSHDIR}
    ADD ssh/config ${SSHDIR}/config
    ADD ssh/id_rsa.mpi ${SSHDIR}/id_rsa
    ADD ssh/id_rsa.mpi.pub ${SSHDIR}/id_rsa.pub
    ADD ssh/id_rsa.mpi.pub ${SSHDIR}/authorized_keys
    
    # Step 7
    RUN chmod -R 600 ${SSHDIR}* && \
        chown -R $USER1:$USER1 ${SSHDIR} && \
        chown -R $USER1:$USER1 /etc/ssh && \
        chown -R $USER1:$USER1 /usr/local/lib/python2.7
        
    # Step 8
    RUN sed -i 's|Port 22|Port 2222|g' /etc/ssh/sshd_config
    USER $USER1
    RUN chmod 600 ${SSHDIR}/*
    EXPOSE 2222
    
    # Step 9
    CMD ["/usr/sbin/sshd", "-D"]

The above Dockerfile builds a docker image with python and an exposed SSH server.

The steps above are explained below:

1. Build time arguments set to the UID and username of the user who will submit the job

2. Required software installed and ssh directory created

3. Required changes made to allow ssh execution in Docker container

4. Required environment variables set

5. Create user using build time arguments UID and USER, create home directory for user.

6. Create ssh directory in user dir, add config and identity files

7. Change ownership of ssh directory to new user

8. Set ssh service port to 2222, only root has access to port 22, any scripts accessing an
   image on the above, must specify port 2222. Change run time user to our new user

9. Set ssh server to run at startup

The files added to the image can be viewed from the "docker_images/pyssh/ssh" directory

To build the above image, run ``` docker build --build-arg UID=$(id -u $USER) --build-arg USER=$USER -t pyssh . ```

## What does the job do?

Our example job will take some email data in mongodb .bson format. We will have four
containers, one master for co-ordinating workload, a mongodb container to store the .bson
data, and two worker nodes for carrying out the processing. The worker nodes will count
the number of relays a user has had for each day, and print the info to stdout.

Our Docker definition file will look like this:

    {"hostfile_format": "json",
      "containers":[{
          "interactive": "True",
          "image": "testcluster:5000/dgrid.pyssh",
          "name": "head",
          "environment_variables": [
            "DBUSER=user",
            "DBNAME=sendmail",
            "DBPASS=password",
            "COLLECTION=logins",
            "DB_PORT=27017",
            "DUMPFILE=/dump.bson",
            "HOSTFILE=/hostfile.json"],
          "volumes": [
            "/home/user/mongo-job/mongo_job.py:/mongo_job.py",
            "/home/user/mongo-job/logins.bson:/dump.bson"],
          "host_list_location": "/",
          "run_cmd": ["python", "-u", "/mongo_job.py"]
        },
        {
          "interactive": "False",
          "image": "testcluster:5000/dgrid.pyssh",
          "name": "worker",
          "volumes": [
            "/home/user/mongo-job/data_analysis.py:/data_analysis.py"],
          "scale": 2,
          "host_to_list": ["tag=workers"]
        },
        {
          "interactive": "False",
          "image": "testcluster:5000/dgrid.mongodb",
          "name": "database",
          "environment_variables": [
            "MONGODB_USER=user",
            "MONGODB_DATABASE=sendmail",
            "MONGODB_PASS=password",
            "AUTH=no"],
          "host_to_list": ["tag=database"]
        }
      ]
    }

The mongo_job.py script is as follows:

    import bson, json, os, pymongo
    from pymongo import MongoClient
    import threading
    from fabric.api import run, env
    from fabric.tasks import execute
    from fabric.network import disconnect_all
    from retry import retry
    import paramiko
    
    def read_hostfile(hostfile):
        with open(hostfile) as hf:
            data = json.load(hf)
    
        for host in data['database']:
            db_host = host.decode('utf-8')
        
        workers = []
        
        for worker in data['workers']:
            workers.append(worker.decode('utf-8'))
            
        return db_host, workers
        
    def read_dump(dump):
        with open(dump,'rb') as f:
            return bson.decode_all(f.read())
            
    def populate_database(db_host, db_port, user, password, database, dataset, data):
        db = make_connection(db_host, db_port, user, password, database)
        collection = db[dataset]
        result = collection.insert_many(data)
        dataset_size = len(result.inserted_ids)
    
    @retry(pymongo.errors.OperationFailure, tries=3, delay=5)
    def make_connection(db_host, db_port, user, password, database):
        client = MongoClient(db_host, db_port)
        db = client[database]
        db.authenticate(user, password)
        return db
    
    def run_analysis(workers):
        threads = []
        threads.append(threading.Thread(target=worker, args=(11, workers[0] + ":2222")))
        threads.append(threading.Thread(target=worker, args=(12, workers[1] + ":2222")))
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
    def worker(month, host):
        env.reject_unknown_hosts = False
        env.disable_known_hosts = True
        env.user = "CONATINER_USERNAME"
        env.password = "CONTAINER_PASSWORD"
        execute(job, month, host=host)
    
    def job(month):
        run("python /data_analysis.py -y 2016 -m %i -dbh %s -dbp %s -dbn %s -col %s -dbu %s -dbport %i " % (month, db_host, password, database, dataset, user, db_port))
        
    if __name__ == '__main__':
    
        hostfile = os.environ['HOSTFILE']
        db_port = int(os.environ["DB_PORT"])
        database = os.environ["DBNAME"]
        dump = os.environ["DUMPFILE"]
        dataset = os.environ["COLLECTION"]
        user = os.environ["DBUSER"]
        password = os.environ["DBPASS"]
    
        db_host, workers = read_hostfile(hostfile)
        
        data = read_dump(dump)
        
        populate_database(db_host, db_port, user, password, database, dataset, data)
        run_analysis(workers)
        
The data_analysis.py file is as follows:

    import bson, json, os, pymongo
    from pymongo import MongoClient
    import argparse, datetime, calendar
    
    def analyse_month(year, month):
        client = MongoClient(db_host, db_port)
        db = client[database]
        db.authenticate(user, passw)
        collection = db[dataset]
        
        days_in_month = calendar.monthrange(int(year),int(month))[1]
        for d in range(1, days_in_month):
            start_date = datetime.datetime(int(year), int(month), d, 00)
            next_date = datetime.datetime(int(year), int(month), d+1, 00)
            data = collection.find({"dstamp": {"$gt": start_date, "$lt": next_date}})
            
            print("## DATA for month %i day %i" % (int(month), int(d)))
            analyse_logins(data)
            
    def analyse_logins(data):
        unique_user_logins = dict()
        for login in data:
            author = login['authid']
            if author not in unique_user_logins:
                unique_user_logins[author] = [login['relay']]
            else:
                unique_user_logins[author].append(login['relay'])
                
        for user in unique_user_logins:
            unique_relay = 1
            first_relay = unique_user_logins[user][0]
            for relay in range(1, len(unique_user_logins[user])):
                if relay is not first_relay:
                    unique_relay += 1
                  
            print("USER: %s, had %i unique relays" % (user, unique_relay))
        
    
    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument('-y', dest='y')
        parser.add_argument('-m', dest='m')
        parser.add_argument('-dbh', dest='dbh')
        parser.add_argument('-dbp', dest='dbp')
        parser.add_argument('-dbn', dest='dbn')
        parser.add_argument('-col', dest='col')
        parser.add_argument('-dbu', dest='dbu')
        parser.add_argument('-dbport', dest='dbport')
        args = parser.parse_args()
    
        db_port = int(args.dbport)
        db_host = args.dbh
        database = args.dbn
        dataset = args.col
        user = args.dbu
        passw = args.dbp
    
        analyse_month(args.y, args.m)
        
### Some explanatory text about the job 
I will not explain the function of all the code, instead I'll explain some of the intricacies
that need to be overcome, with job execution in containers and how they relate to the sections in the code.
For libraries used that you're not familiar with.....read the documentation for them.

__Database initialization__

In mongo_job.py the make_connection method, is set to retry on failure. When the database container starts
it has to initialise databases and user logins, the master container will not know, when this has completed,
so when making a connection, it will retry until the database has fully initialized. The time for the database
to initialize should be relatively small, i.e. one retry at most generally.

__Worker execution__

To make the workers execute simultaneously, we create a thread for each worker and call execute for both threads.

__Environment variables__

You may wonder, why variables like the database hostname, username, password etc. are'nt passed as environment 
variables to worker containers. When environment variables are set for a container, they will be set up in the 
runtime shell of the container, in the case of worker nodes, the shell that runs the ssh server.

When the master container SSH's into a worker the newly created shell does not container those environment variables,
so all required environment variables, are passed to the worker nodes by the master container, on execution of the
data_analysis.py script instead.

__Reading the hostfile__

An example of reading the json formatted hostfile, like getting hosts based on the assigned tag, can be seen in
mongo_job.py's read_hostfile() method.

__SSH port numbers__

Note in mongo_job.py's run_analysis() method, the port number ":2222" is appended to each hostname, so that
the fabric library will use port 2222 for ssh instead of 22, which isn't used by our PySSH image.

## What to take from this example?

1. You cannot run as root within the container:
  * Custom images must be created for use on Torque with usernames and UID's set to the UID and usernames of people
    on the cluster who will submit jobs.
   
  * A registry should be created for storing these custom images.
  
  * Technically, all images used will have to be custom, as most images on Dockerhub run as root by default
   
2. In custom images, the new users should have ownership over all binaries and files that'll be used during execution.

3. Volumes should never be created in Dockerfiles, as they are always owned by root, any volumes you need should be 
   volumes mounted from a user's home directory at run time.
   
4. When creating SSH containers, use ports that are not owned by root for exposing the SSH service.

5. Environment variables set in Docker definition files will not persist across shells in the containers.
   They will only exist in the runtime shell, created at container startup.
   
6. When using databases, there will be some time until the database becomes usable by other containers.

Hopefully, this example gives a relatively clear overview of how to create images for Torque execution with DGrid,
the intricacies of Docker with Torque and how to overcome them, and an idea of use cases for DGrid with Torque.