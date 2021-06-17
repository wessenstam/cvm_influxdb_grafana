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
    
    Make sure that everybody has read/write access to the directory in which InfluxDB and Grafana write thier data. This can be done via ```chmod 777 -R ${PWD}/docker_data/``` for Linux and MacOS. Forgetting this step will lead into not starting the Grafana container.

3. Run ``docker-compose create`` to get the containerized environment build according to the yaml file
4. Run ``docker-compose up -d`` to start the just created environment.

### InfluxDB

1. Open a browser window to http://<IP ADDRESS OF DOCKER HOST>:8086 and configure InfluxDB
2. Remember the username, password, Initial Organization Name and Initial Bucket Name as they are needed later in the parameters section.
3. Get the token via **Quick Start -> Data -> Python**
4. Something like below will be shown:

    ```python
    from datetime import datetime

    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS

    # You can generate a Token from the "Tokens Tab" in the UI
    token = "UrBMNS04-SgCPGZOoFlww1EIo2UKz-LqhBB-LGSGTL6SqTL-1zn3Uyll7k-qR_q2Mx5YQeVIx8peSWx1y44ZcA=="
    org = "performance"
    bucket = "cvms"

    client = InfluxDBClient(url="http://10.42.13.155:8086", token=token)
    ```

5. The token (we need later), not including the double quotes, using the example from the above, is: **UrBMNS04-SgCPGZOoFlww1EIo2UKz-LqhBB-LGSGTL6SqTL-1zn3Uyll7k-qR_q2Mx5YQeVIx8peSWx1y44ZcA==**

### Grafana - Initial config

1. Open a browser window to http://<IP ADDRESS OF DOCKER HOST>:3000 and configure Grafana. Default username/password is admin/admin
2. Change the admin password to something of your choice
3. After the UI opens, click on the left hand side of the UI the **cog icon -> Data sources**
4. Click **Add data source -> InfluxDB**
5. Set these parameters:

   1. **Query language** - Flux
   2. **URL** - http://<IP ADDRESS OF DOCKER MACHINE>:8086
   3. **Auth** - Enable *Basic auth* (if not enabled)
   4. **User** - Your InfluxDB username
   5. **Password** - The corresponding user's password
   6. **InfluxDB Details**
      
      1. **Organization** - Your configured organization
      2. **Token** - The token you saw earlier
      3. **Default Bucket** - The earlier created bucket
    
   7. Click **Save & Test**
   8. Just above the button, if entered the correct information, a Green backgrounded tick should be shown as well as **3 buckets found**
   9. Your Grafana instance can now use the InfluxDB

## Parameters needed

For the tools, server and probe side, to run, parameters must be used. The parameters need to be put in a file called **env.list**. The file needs to contain the following parameters and values:

1. server_ip = IP of the server part of the measurement tool
2. server_prt= port on which the server is listening (default port 5000)
3. user_name = The username for the API connection to the Nutanix Cluster
4. passwd = Corresponding password for the API connection ot the Nutanix Cluster
5. token = Token to access the InfluxDB server
6. db_server = IP addess of the InfluxDB server, if runing as a container, this si the IP address of the Machine running the container
7. org = Organisation as defined in InfluxDB
8. bucket = The name of the bucket as defined in the InfluxDB## Running the probe server

An example for the **env.list** file is

``` bash
    # Variables for the probe_server and probe containers
    server_ip=1.1.1.1
    server_prt=5000
    user_name=admin
    passwd=PASSWORD
    db_server=2.2.2.2
    token=UrBMNS04-SgCPGZOoFlww1EIo2UKz-LqhBB-LGSGTL6SqTL-1zn3Uyll7k-qR_q2Mx5YQeVIx8peSWx1y44ZcA==
    org=performance
    bucket=cvms
```

## Running the probe server

Run the probing server using the below command:

```docker run -d --rm --name probe-server -v ${PWD}:/code --env-file ./env.list -p 5000:5000 probe_server```

This command runs the probe server container and it is listening on port 5000 on the machine that is running the container. Also it uses the "environmental variables" as mentioned in the **env.list** file.

## Running probe(s)

Run the probe(s) using the below command:

```docker run -d --rm --name probe -v ${PWD}:/code --env-file ./env.list -e check_ip=<IP ADDRESS OF PE> probe```

This command runs the probe container and it uses the "environmental variables" as mentioned in the **env.list** file. Besides those parameter and extra parameter is added. ``-e check_ip=<IP ADDRESS OF PE>`` is pointing to the IP address of one cluster. if there are multiple cluster, rerun the command using another IP address(ess) for the other cluster(s)