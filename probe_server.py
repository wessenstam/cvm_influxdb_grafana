# Python Flask server for the probe to have their measurements writen into a InfluxDB for use with Grafana
# Willem Essenstam - Nutanix - 23-01-2021

import json
from flask import *
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

# Get the InfluxDB Client session up and running
# You can generate a Token from the "Tokens Tab" in the UI
token = os.environ['token']
org = os.environ['org']
bucket = os.environ['bucket']
db_server=os.environ['db_server']
client = InfluxDBClient(url="http://"+db_server+":8086", token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)


# Get the json data from the probes into a dataframe.
@app.route("/", methods=['POST'])
def input_json():
    json_data=request.get_json()
    name=json_data['cvm_name']
    cpu=json_data['cpu']
    cpu_ready=json_data['cpu_ready']
    ram=json_data['ram']
    io_read=json_data['io_read']
    io_write=json_data['io_write']
    write_api.write(bucket, org, [
            {"measurement": "performance", "tags": {"cvm-name": name}, "fields": {"cpu": float(cpu),"cpu_ready": float(cpu_ready),"ram": float(ram),"io_read": float(io_read),"io_write": float(io_write)}}])
    return_payload={'name':name,'cpu':cpu,'cpu_ready':cpu_ready,'ram':ram,'io_read':io_read,'io_write':io_write}
    return json.dumps(return_payload)
    
@app.route("/", methods=['GET'])
def input():

    return " "
# *************************************************************************************************
if __name__ == "main":
    # start the app
    app.run()