import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import glob
import os
import textwrap
from datetime import datetime
import csv
import json
from flask import send_file

def wrap_labels(ax, width, break_long_words=False):
    labels = []
    for label in ax.get_xticklabels():
        text = label.get_text()
        labels.append(textwrap.fill(text, width=width,
                      break_long_words=break_long_words))
    ax.set_xticklabels(labels, rotation=0)

def create_chart(time_1, value_1, time_2, value_2, filename):
    if len(time_1) > len(time_2):
        timestamp = time_1
    else:
        timestamp = time_2

    fig, ax = plt.subplots(1,1, figsize=(15, 6))
    plt.xticks(fontsize=6)
    plt.xticks(range(len(timestamp)), timestamp)
    plt.plot(value_1)
    plt.plot(value_2)
    plt.legend(['predicted', 'ground_truth'])
    length = len(timestamp)
    ticker_spacing = length/15
    wrap_labels(ax, 10)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(int(ticker_spacing)))
    plt.title(filename)
    plt.savefig("chart/" + filename + '.jpg')
    plt.show()

def check_folder():
    filepath =  os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
    files = glob.glob("chart/*.jpg")
    files.sort(key=os.path.getmtime, reverse=True)
    while(len(files) > 30):
        filename = files.pop()
        os.remove(filepath + '/' + filename)
    return(files)

def get_history(algo, dataset, device, startdate, enddate, filepath, filename):
    if(os.path.isfile(filepath + filename + ".jpg" )):
        return send_file(filepath + filename + ".jpg")
    else:
        predicted_times = []
        predicted_values = []

        with open('./csv/' + algo + '/' + algo + '_' + dataset + '_' + device + '_predicted.csv', 'r', encoding="utf-8") as file_name:
            csvReader = csv.reader(file_name)
            is_first_row = 1
            row_id = 0

            for row in csvReader:
                if row_id not in [0, 1, 2]:
                    if row_id%300 == 0:
                        if datetime.strptime(startdate, '%Y-%m-%d %H:%M:%S%z') <= datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S%z') <= datetime.strptime(enddate, '%Y-%m-%d %H:%M:%S%z'):
                            if datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S%z') > datetime.strptime(enddate, '%Y-%m-%d %H:%M:%S%z'):
                                break
                            else:
                                predicted_times.append(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S%z'))
                                predicted_values.append(float(row[1]))
                row_id += 1

        ground_truth_times = []
        ground_truth_values = []

        with open('./csv/' + algo + '/' + algo + '_' + dataset + '_' + device + '_ground_truth.csv', 'r', encoding="utf-8") as file_name:
             csvReader = csv.reader(file_name)
             is_first_row = 1
             row_id = 0

             for row in csvReader:
                 if row_id not in [0, 1, 2]:
                     if row_id%300 == 0:
                         if datetime.strptime(startdate, '%Y-%m-%d %H:%M:%S%z') <= datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S%z') <= datetime.strptime(enddate, '%Y-%m-%d %H:%M:%S%z'):
                             if datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S%z') > datetime.strptime(enddate, '%Y-%m-%d %H:%M:%S%z'):
                                 break
                             else:
                                 ground_truth_times.append(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S%z'))
                                 ground_truth_values.append(float(row[1]))
                 row_id += 1

        if len(ground_truth_times) == 0:
            return "period of time has no value", 400
        create_chart(predicted_times, predicted_values, ground_truth_times, ground_truth_values, filename)

        return send_file(filepath + filename + ".jpg")

def get_json(algo, model, plug):
    filepath = "./flower/" + algo + '/'
    filename = algo + '.json'
   
    f = open(filepath + filename)
    arr = json.load(f)
    return str(123)


