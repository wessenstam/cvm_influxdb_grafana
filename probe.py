# This script is to probed the to be checked cluster
# 16-06-2021: Willem Essenstam - Initial version 0.1


import requests
import json
import urllib3
import time
import os

#####################################################################################################################################################################
# This function is to get the to see if the initialisation of the cluster has been run (EULA, PULSE, Network)
#####################################################################################################################################################################
def get_json_data(ip_address,get_url,json_data,method,user,passwd):
    #Get the URL and compose the command to get the request from the REST API of the cluster
    if not "http:" in get_url:
        url="https://"+ip_address+":9440/"+get_url
    else:
        url=get_url    
        
    header_post = {'Content-type': 'application/json'}
    # Set the right requests based on GET or POST
    if method == "get":
        try:
            page=requests.get(url,verify=False,auth=(user,passwd),timeout=15)
            page.raise_for_status()
            json_data = json.loads(page.text)
            return json_data
        except requests.exceptions.RequestException as err:
            print("OopsError: Something Else", err)
            return err
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
    else:
        try:
            page=requests.post(url, verify=False, auth=(user, passwd), data=json_data, headers=header_post,timeout=15)
            page.raise_for_status()
            json_data = json.loads(page.text)
            return json_data
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except reqcheck_ipuests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)


#####################################################################################################################################################################
# Data grabs from the server
#####################################################################################################################################################################

def grab_data(server_ip,user,passwd,uuid):
    # Set some variables
    pe_ip = server_ip
    method="get"
    payload=""
    cvm_uuid=uuid

    
    # *********************************************************************************************************
    # What is the name of the CVM?
    url = "PrismGateway/services/rest/v1/vms/"+cvm_uuid
    json_search = get_json_data(pe_ip, url, payload, method, user, passwd)
    name = json_search['vmName']   

    # *********************************************************************************************************
    # What is the current CPU value for the CVM?
    url = "PrismGateway/services/rest/v1/vms/"+cvm_uuid
    json_search = get_json_data(pe_ip, url, payload, method, user, passwd)
    cpu = str(round(int(json_search['stats']['hypervisor_cpu_usage_ppm'])/10000,2))


    # *********************************************************************************************************
    # What is the current CPU Ready value for the CVM?
    url = "PrismGateway/services/rest/v1/vms/"+cvm_uuid
    json_search = get_json_data(pe_ip, url, payload, method, user, passwd)
    cpu_ready = str(round(int(json_search['stats']['hypervisor.cpu_ready_time_ppm'])/10000,2))

    # *********************************************************************************************************
    # What is the current RAM usage value for the CVM?
    url = "PrismGateway/services/rest/v1/vms/"+cvm_uuid
    json_search = get_json_data(server_ip, url, payload, method, user, passwd)
    ram = str(round(int(json_search['stats']['memory_usage_ppm'])/10000,2))

    # ********************************************************************************************************
    # What is the current IOPS Read value for the CVM?
    url = "PrismGateway/services/rest/v1/vms/"+cvm_uuid
    json_search = get_json_data(server_ip, url, payload, method, user, passwd)
    io_read = str(round(int(json_search['stats']['controller_read_io_ppm'])/10000,2))

    # ********************************************************************************************************

    # What is the current IOPS Write value for the CVM
    url = "PrismGateway/services/rest/v1/vms/"+cvm_uuid
    json_search = get_json_data(server_ip, url, payload, method, user, passwd)
    io_write = str(round(int(json_search['stats']['controller_num_write_io'])/10000,2))

    # ********************************************************************************************************

    # Combine all variables in a JSON file so we can send it to the server
    json_payload='{"cpu":"'+str(cpu)+ \
                 '","cpu_ready":"'+str(cpu_ready)+ \
                 '","ram":"'+str(ram)+ \
                 '","io_read":"'+str(io_read)+ \
                 '","io_write":"' + str(io_write) + \
                 '","cvm_name":"'+str(name) +\
                 '"}'

    # ********************************************************************************************************
    # Return the combined JSON so it can be send
    return json_payload

#####################################################################################################################################################################
# Function for getting the UUIDs of the CVM in the cluster
#####################################################################################################################################################################
def get_uuid_cvms(server_ip,user,passwd):
    # Set some variables
    pe_ip = server_ip
    method="get"
    payload=""

    # What is the name of cluster so we can search in the data we send?
    url = "PrismGateway/services/rest/v1/vms?filterCriteria=is_cvm==1"
    json_search = get_json_data(pe_ip, url, payload, method, user, passwd)
    cvm_nr=json_search['metadata']['totalEntities']
    cvm_uuids=[]
    for cvm in range(cvm_nr):
        cvm_uuid=json_search['entities'][int(cvm)-1]['vmId']
        cvm_uuids.append(cvm_uuid)
    return cvm_uuids


#####################################################################################################################################################################
# __main__
#####################################################################################################################################################################
# Take the SSL warning out of the screen
urllib3.disable_warnings()

# Grab the environmental data we have received when we started the container
server_ip=os.environ['server_ip']
server_prt=os.environ['server_prt']
check_ip=os.environ['check_ip']
user_name=os.environ['user_name']
passwd=os.environ['passwd']
value=''
method='post'
server_url="http://"+str(server_ip)+":"+str(server_prt)+"/"

# Grab the UUIDS for the CVMs from the cluster
cvm_uuids=get_uuid_cvms(check_ip,user_name,passwd)

# Grab the data for all CVMs
while True:
    for cvm_uuid in cvm_uuids:
        json_return=grab_data(check_ip,user_name,passwd,cvm_uuid)
        get_json_data(server_ip,server_url,json_return,"POST",user_name,passwd)
    
    time.sleep(30)