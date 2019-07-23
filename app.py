from flask import Flask
from flask import render_template
from pymongo import MongoClient
import json
from bson import json_util
from bson.json_util import dumps
import dns # required for connecting with SRV
import csv
from pathlib import Path

app = Flask(__name__)

URI_string = "mongodb+srv://explorer:1234567890@datacenter-nfv4t.gcp.mongodb.net/test?retryWrites=true&w=majority"

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/Loans/SummerTraining")
def donorschoose_projects():
    connection = MongoClient(URI_string)
    collection = connection["loans_data_base"]["data"]
    projects = collection.find( {}, {"_id" : False, "funded_amnt" : True, "int_rate" : True, "emp_length" : True,
        "annual_inc" : True,"loan_status" : True, "num_sats" : True, "last_pymnt_amnt" : True,
        "avg_cur_bal" : True, "addr_state" : True }) 
    json_projects = []
    for project in projects:
        json_projects.append(project)
    json_projects = json.dumps(json_projects, default=json_util.default)
    connection.close()
    return json_projects

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)