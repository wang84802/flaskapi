from flask import Flask, request, send_file, abort
from flask_cors import CORS
from google.cloud import bigquery
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from chartapi import create_chart, check_folder
import logging
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./chris-project-364416-2cbb3d0fd013.json" # awin gcp account
app = Flask(__name__)
CORS(app)

# @app.before_request
def limit_remote_addr():
    allow_ip = ['192.168.1.195', '54.86.50.139']
    if request.remote_addr not in allow_ip:
        abort(403)  # Forbidden

@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return request.remote_addr, 200

@app.route('/test')
def test():
    list1 = check_folder()
    return str(list1)

@app.route('/')
def hello():
    return "Hello"

@app.route('/get_chart')
def query():
    check_folder()

    algo      = request.args.get('algo')
    dataset   = request.args.get('dataset')
    device    = request.args.get('device')
    startdate = request.args.get('startdate')
    enddate   = request.args.get('enddate')
   
    algo_list   = ['DAE', 'GRU', 'RNN', 'ShortSeq2Point']
    dataset_list = ['iawe', 'redd', 'ukdale']
    iawe_device_list   = ['clothes_iron', 'fridge', 'washer_dryer']
    redd_device_list   = ['fridge', 'microwave', 'socket']
    ukdale_device_list = ['kettle', 'microwave', 'washer_dryer']

    if algo not in algo_list:
        return "algo not found", 404
    elif dataset not in dataset_list:
        return "dataset not found", 404
    elif (dataset == "iawe" and device not in iawe_device_list) or (dataset=="redd" and device not in redd_device_list) and (dataset == "ukdale" and device not in ukdale_device_list):
        return "device not found", 404

    app.logger.info('test')
    filepath = "./chart/"
    filename = algo + "_" + dataset + "_" + device + "_" + startdate + "_" + enddate

    if(os.path.isfile(filepath + filename + ".jpg" )):
        return send_file(filepath + filename + ".jpg")
    else:
        string_1 = "SELECT * FROM `chris-project-364416." + algo + "." + dataset + "_" + device + "_predicted` where time between '" + startdate + "' and '" + enddate + "' and time = DATE_TRUNC(time, HOUR) order by time;"
        string_2 = "SELECT * FROM `chris-project-364416." + algo + "." + dataset + "_" + device + "_ground_truth` where time between '" + startdate + "' and '" + enddate + "' and time = DATE_TRUNC(time, HOUR) order by time;"

        client = bigquery.Client()
        query_job_1 = client.query(string_1)
        query_job_2 = client.query(string_2)
        time_1 = []
        time_2 = []
        value_1 = []
        value_2 = []

        results_1 = query_job_1.result()
        results_2 = query_job_2.result()
        for i, index in enumerate(results_1):
            time_1.append(index['time'].strftime("%Y/%m/%d\n%H:%M:%S"))
            value_1.append(index['predicted'])

        for i, index in enumerate(results_2):
            time_2.append(index['time'].strftime("%Y/%m/%d\n%H:%M:%S"))
            value_2.append(index['ground_truth'])
    
        create_chart(time_1, value_1, time_2, value_2, filename)
        return send_file(filepath + filename + ".jpg")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
