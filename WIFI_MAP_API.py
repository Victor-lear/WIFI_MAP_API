# -*- coding: utf-8 -*-
from flask import Flask, jsonify,request
from flask_cors import CORS

import time
import json
from requests import get
from pymongo import MongoClient
import os
import pandas as pd
from datetime import datetime
from datetime import timedelta
from datetime import date
from dotenv import load_dotenv
app = Flask(__name__)
CORS(app)
load_dotenv()
mongo_url_01=os.getenv('MongoClient')

# 获取公共IP地址
#PUBLIC_IP = get('https://api.ipify.org/').text
def getmongodata(value):
    global mongo_url_01
    start_time = datetime.strptime(value, "%Y-%m-%d")
    end_time = start_time.replace(year=start_time.year , hour=23, minute=59, second=59, microsecond=0)
    search_data = {"start_time": {"$gte": start_time, "$lte": end_time}}
    conn = MongoClient(mongo_url_01)
    db = conn['Client']
    collection = db['path']
    cursor = collection.find(search_data)
    data = [d for d in cursor]
    return data
def getmongodata_build(value):
    global mongo_url_01
    start_time = datetime.strptime(value, "%Y-%m-%d")
    end_time = start_time.replace(year=start_time.year , hour=23, minute=59, second=59, microsecond=0)
    search_data = {"DateTime": {"$gte": start_time, "$lte": end_time}}
    conn = MongoClient(mongo_url_01)
    db = conn['AP']
    collection = db['hour_count']
    cursor = collection.find(search_data)
    data = [d for d in cursor]
    return data

def get_time_data():
    data = []
    for i in range(1,32):
        current_date = date.today()
        delta = timedelta(days=i)
        previous_date = current_date - delta
        data.append({"time": str(previous_date)})
    return data

def get_path_data(value):
    data=getmongodata(value)

    import_data = {'data': {}}
    for i in range(len(data)):
        path_data = [0 for _ in range(24)]
        path = str(data[i]['path'])
        date_object = data[i]['start_time']
        year = date_object.year
        month = date_object.month
        day = date_object.day
        hour = date_object.hour
        year_str = str(year)
        month_str = str(month).zfill(2)
        day_str = str(day).zfill(2)
        hour_int = int(hour)
        time = f"{year_str}-{month_str}-{day_str}"

        if time not in import_data['data']:
            import_data['data'][time] = {}

        if path not in import_data['data'][time]:
            import_data['data'][time][path] = path_data

        import_data['data'][time][path][hour_int] = data[i]['num']

    return import_data
def get_build_data(value):
    data=getmongodata_build(value)
    import_data = {'data': {}}
    for i in range(len(data)):
        path_data = [0 for _ in range(24)]
        path = str(data[i]['ap_name'])
        date_object = data[i]['DateTime']
        year = date_object.year
        
        month = date_object.month
        day = date_object.day
        hour = date_object.hour
        year_str = str(year)
        month_str = str(month).zfill(2)
        day_str = str(day).zfill(2)
        hour_int = int(hour)
        time = f"{year_str}-{month_str}-{day_str}"

        if time not in import_data['data']:
            import_data['data'][time] = {}

        if path not in import_data['data'][time]:
            import_data['data'][time][path] = path_data

        import_data['data'][time][path][hour_int] = data[i]['sta_count_avg']+import_data['data'][time][path][hour_int]

    return import_data
@app.route('/gettime', methods=['GET'])

def get_time():
    try:
        time_data = get_time_data()
        send_data = {"data": time_data}
        res = json.dumps(send_data)
        return res
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/getpath', methods=['POST'])
def get_path():
    try:
        json_data = request.get_json()

        if json_data is not None:
            for key, value in json_data.items():
                res = get_path_data(value)
                return jsonify(res)
        else:
            return jsonify({"error": "Invalid JSON data in the request"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/getbuild', methods=['POST'])
def get_build():
    try:
        json_data = request.get_json()

        if json_data is not None:
            for key, value in json_data.items():
                res = get_build_data(value)
                return jsonify(res)
        else:
            return jsonify({"error": "Invalid JSON data in the request"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    with open('server.json', 'r') as file:
        data = json.load(file)
    app.run(host=data['host'], port=data['port'])
