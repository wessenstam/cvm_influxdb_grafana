# CVM Monitoring tool

This Repo exists out of four tools

1. probe_server.py, server side of the measurement tool
2. probe.py, probe side of the measurement tool
3. Independent InfluxDB for storing measurement data
4. Independent Grafana for showing dashboards

## probe_server.py
Python source code of the server side of solution for the performance of the CVMs in a cluster. Receives data from the probe(s) and stores it into an InfluxDB. Will be run containerized. To run natively on Linux VMs, the corresponding dockerfile (Dockerfile-Server) is providing the dependencies needed.
## probe.py
Probe side that grabs the performance info from the cluster it checks and sends the data to the server side. Checks data every 5 minutes. Every probe will be checking 1 cluster. THis coud lead into many probe containers to be active at one time
# Usage

This chapter is describing what the pre-requirements are and how the tool should be used.
## Prerequisites

As the tools is made out of Docker containers, docker needs to be installed on the machine that will run the containers. The internet has lots of articles on how to install Docker on the O/S of your choice.

By using Github, it is possible to pull the latest version on any machine. Therefore also git needs to be installed on the mahcine so the repo can be cloned. Depending on the use case, using a separate InfluxDb and/or Grafana environment, docker-compose also needs to be installed. The Github repo includes a docker-compose YAML file to start and run such an environemnt as Docker containers with persistent storage.
## Getting the files needed for the tool
To grab the needed files, follow these steps:

1. Create a directory in which you want to store the files from the cloned repo, but also the files for InfluxDB and Grafana (persistent storage) (example /docker-data/)
2. ``cd`` into the newly created directory
3. Run ``git clone https://github.com/wessenstam/cvm_influxdb_grafana``. this will clone the dat from the repository on Github
4. ``cd`` into the repo cloned directory (cvm_influxdb_grafana)

## Build the containers

As the tool is container based, use the Dockerfile-Server and Dockerfile-Probe dockerfiles, using ``docker build -f <NAME OF THE FILE> -t <TAG NAME>`` to build the containers. The commands that are shown are examples. Exchange ``probe_xx`` to your name.

## Parameters needed

For the tools, server and probe side, to run, parameters must be used. The parameters need to be put in a file called **env.list**. The file needs to contain the following parameters and values:

1. server_ip = IP of the server part (server.py) of the measurement tool
2. server_prt= port on which the server is listening (default 5000, FLASK port)
3. user_name = The username for the connection to the Nutanix Cluster (admin)
4. passwd = Corresponding password for the connection ot the Nutanix Cluster
5. token = Token to access the InfluxDB server
6. db_server = IP addess of the InfluxDB server, if runing as a container, this si the IP address of the Machine running the container
7. org = Organisation as defined in InfluxDB
8. bucket = The name of the bucket as defined in the InfluxDB

## Running with a separate InfluxDB and Grafana environment
This chapter is only needed if the tool is not using an existing InfluxDB and Grafana emvironment by using InfluxDB and Grafana as containers.

1. Check docker-compose is installed on the machine by typing ``docker-compose``. If not installed, install it.
2. The current content of the cloned docker-compose.yaml file is

   ```bash
    version: '3'

    services:
      grafana:
        image: grafana/grafana
        container_name: grafana
        depends_on:
          - influxdb
        ports:
          - 3000:3000
        volumes:
          - ${PWD}/docker_data/grafana_data:/var/lib/grafana
        restart: always
    
      influxdb:
        image: quay.io/influxdb/influxdb:v2.0.7
        container_name: influxdb
        ports:
          - 8086:8086
        volumes:
          - ${PWD}/docker_data/influxdb:/root/.influxdbv2/
        restart: always
    ```
    This will create persistent data stores for InfluxDB and Grafana under the **current directory/docker-data** via the **${PWD}** parameter. Change this parameter if it should be stored somewhere else by opening the file and saving it.

3. Run ``docker-compose create`` to get the containerized environment build according to the yaml file

## Running the probe server
Run the probing server using the below command where the following parameters must be set:

``docker run -d --rm --name probe-server --env-file ./env.list -p 5000:5000 probe_server``


## Tools starting order

The order of starting the tools is
1. InfluxDB and Grafana
2. Configure InfluxDB and Grafana
3. Grab the InfluxDB Token, Org and Bucket from the InlfuxDB interface
4. Start the probe_server container
5. Start the probe container
