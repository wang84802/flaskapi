from flask import Flask, request, send_file, abort, jsonify
from flask_cors import CORS
from google.cloud import bigquery
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from chartapi import create_chart, check_folder, get_history, get_json
from datetime import datetime
import os
import csv
import json
import logging

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
def get_history_data():
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

    filepath = "./chart/"
    filename = algo + "_" + dataset + "_" + device + "_" + startdate + "_" + enddate

    startdate = startdate + ' 00:00:00+05:30'
    enddate = enddate + ' 00:00:00+05:30'
   
    str(datetime.strptime(startdate, '%Y-%m-%d %H:%M:%S%z'))

    return get_history(algo, dataset, device, startdate, enddate, filepath, filename)

@app.route('/get_electric_anaylsis_data')
def get_electric_anaylsis_data():
  
    algo      = request.args.get('algo')
    model     = request.args.get('model')
    plug      = request.args.get('plug')
    
    algo_list  = ['flower', 'non-flower', 'differential-privacy']
    model_list = ['DAE', 'AttentionCNN', 'GRU', 'ShortSeq2Point', 'RNN', 'WindowGRU', 'SGN', 'CNNLSTM', 'Energan']
    plug_list  = ['plug1-1', 'plug1-2', 'plug1-3', 'plug2-1', 'plug2-2', 'plug2-3', 'plug3-1', 'plug3-2', 'plug3-3']
    
    if algo not in algo_list:
        return "algo not found", 404
    if model not in model_list:
        return "model not found", 404
    elif plug not in plug_list:
        return "plug not found", 404

    filepath = "./flower/" + algo + '/'
    filename = algo + '.json'

    f = open(filepath + filename)
    arr = json.load(f)
  

    for models in arr['model']:
        if models['modelName'] != model:
            return "model not found", 404
        else:
            for plugs in models['plugName']:
                if plugs['name'] != plug:
                    return "plug not found", 404
                else:
                    return jsonify(plugs['lossfunction'])

@app.route('/get_electric_anaylsis_chart')
def get_electric_anaylsis_chart():

    algo      = request.args.get('algo')
    model     = request.args.get('model')
    plug      = request.args.get('plug')

    model_list = ['DAE', 'AttentionCNN', 'GRU', 'ShortSeq2Point', 'RNN', 'WindowGRU', 'SGN', 'CNNLSTM', 'Energan']
    plug_list  = ['plug1-1', 'plug1-2', 'plug1-3', 'plug2-1', 'plug2-2', 'plug2-3', 'plug3-1', 'plug3-2', 'plug3-3']

    if model not in model_list:
        return "model not found", 404
    elif plug not in plug_list:
        return "plug not found", 404

    filepath = "flower/" + algo + '/' + model + '/'
    filename = model + '_' + plug + '.png'
    try:
        return send_file(filepath + filename)
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
