from pymongo import MongoClient
import json
from bson import json_util
from bson.json_util import dumps
import dns 
import csv
from pathlib import Path
import os
import numpy as np
import pickle
import joblib
from sklearn.preprocessing import PolynomialFeatures 
from flask import Flask, render_template, url_for, request, session, redirect, jsonify, flash
from flask_pymongo import PyMongo
import bcrypt
from wtforms import Form, StringField, PasswordField, validators, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

app = Flask(__name__)
model = pickle.load(open("pickle/vacation_model.pkl","rb"))

URI_string = "mongodb://HamadAlaqeel:hamadA123@cluster0-shard-00-00-c7klj.gcp.mongodb.net:27017,cluster0-shard-00-01-c7klj.gcp.mongodb.net:27017,cluster0-shard-00-02-c7klj.gcp.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority
"

class SignupForm(Form):
    
    Username = StringField('Username', [
        validators.DataRequired(message=('Please enter a username'))
    ])
    
    Email = StringField('Email', [
        validators.DataRequired(),
        validators.Email(message=('Please enter a vaild email address')),
        EqualTo('Email1', message=('Emails must match'))
    ])
    
    Email1 = StringField('Repeat Email',validators=[DataRequired()])
    
    Password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=8, message=('Password should have 8 characters at leats')),
        EqualTo('Password1', message=('Passwords must match'))
    ])
    
    Password1 = PasswordField('Repeat Password',validators=[DataRequired()])

class LoginForm(Form):
    Username = StringField('Username', validators=[DataRequired()])
    Password = PasswordField('Password', validators=[DataRequired()])

@app.route("/")
def index():
    if 'Username' in session:
        return render_template("index.html")
    return render_template("index.html")

@app.route("/statistics")
def statistics():
    if 'Username' in session:
        return render_template("Statistics.html")
    return render_template("Statistics.html")

@app.route('/eligibility')
def eligibility():
    if 'Username' in session:
        return render_template('eligibility.html')
    return render_template("eligibility.html")

@app.route('/InterestRate')
def interestRate():
    if 'Username' in session:
        return render_template('InterestRate.html')
    return render_template("InterestRate.html")
    
def get_prediction(_type, features):
    if _type == 'Home Improvement':
        model = pickle.load(open("pickle/home_improvement.pkl","rb"))
        return model.predict([[features[0],features[1],features[2]]])
    elif _type == 'Car':
        model = pickle.load(open("pickle/car_model.pkl","rb"))
        return model.predict([[features[0],features[1],features[2]]])
    elif _type == 'Credit Card':
        model = pickle.load(open("pickle/credit_card.pkl","rb"))
        return model.predict([[features[0],features[1],features[2]]])
    elif _type == 'Debt Consolidation':
        model = pickle.load(open("pickle/debt_consolidation.pkl","rb"))
        return model.predict([[features[0],features[1],features[2]]])
    elif _type == 'House':
        model = pickle.load(open("pickle/house.pkl","rb"))
        return model.predict([[features[0],features[1],features[2]]])
    elif _type == 'Major Purchase':
        model = pickle.load(open("pickle/major_purchase.pkl","rb"))
        return model.predict([[features[0],features[1],features[2]]])
    elif _type == 'Medical':
        model = pickle.load(open("pickle/medical.pkl","rb"))
        return model.predict([[features[0],features[1],features[2]]])
    elif _type == 'Moving':
        model = pickle.load(open("pickle/moving.pkl","rb"))
        return model.predict([[features[0],features[1],features[2]]])
    elif _type == 'Renewable Energy':
        model = pickle.load(open("pickle/renewable_energy.pkl","rb"))
        return model.predict([[features[0],features[1],features[2]]])
    elif _type == 'Small Business':
        model = pickle.load(open("pickle/small_business.pkl","rb"))
        return model.predict([[features[0],features[1],features[2]]])
    elif _type == 'Vacation':
        model = pickle.load(open("pickle/vacation_model.pkl","rb"))
        return model.predict([[features[0],features[1],features[2]]])
    #others
    else:
        model = pickle.load(open("pickle/others.pkl","rb"))
        return model.predict([[features[0],features[1],features[2]]])

@app.route('/InterestRate', methods=['POST'])
def predict():
    int_features = [request.form['funded_amnt'],request.form['emp_length'],request.form['annual_inc'] ]
    _type = request.form.get('type') 
    try:
        predcition = get_prediction(_type, int_features)
        output = round(predcition[0],2)
        return render_template('InterestRate.html', predcition_text = '%{}'.format(output)  + ' for ' + _type)
    except:
        return render_template('InterestRate.html', predcition_text = "")

@app.route('/addLoan')
def addLoan():
    if 'Username' in session:
        return render_template('addLoan.html')
    return render_template("addLoan.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    
    login_form = LoginForm(request.form) 
    if request.method == 'POST' and login_form.validate():
        connection = MongoClient(URI_string)
        users = connection["SummerTraining"]["Users"]
        login_user = users.find_one({'Username' : request.form['Username']})
        
        if login_user and bcrypt.hashpw(request.form['Password'].encode('utf-8'), login_user['Password']) == login_user['Password']:
            session['Username'] = request.form['Username']
            return redirect(url_for('index'))

        flash('Invalid username/password combination')
        return render_template('login.html', form =login_form)
    return render_template('login.html', form =login_form)

@app.route('/register', methods=['POST', 'GET'])
def register():
    signup_form = SignupForm(request.form) 
    if request.method == 'POST' and signup_form.validate():
        connection = MongoClient(URI_string)
        users = connection["SummerTraining"]["Users"]
        existing_user = users.find_one({'Username' : request.form['Username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['Password'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'Username' : request.form['Username'], 'Email' : request.form['Email'], 'Password' : hashpass})
            session['Username'] = request.form['Username']
            return redirect(url_for('index'))

        flash('Username already exists!')
        return render_template('register.html', form =signup_form)
    return render_template('register.html', form =signup_form)

@app.route('/sign_out')
def sign_out():
    session.pop('Username')
    return redirect(url_for('index'))

@app.route("/Loans/SummerTraining")
def connectCloudDatabases():
    connection = MongoClient(URI_string)
    collection = connection["SummerTraining"]["Loans"]
    projects = collection.find( {}, {"_id" : False, "funded_amnt" : True, "int_rate" : True, "emp_length" : True,
        "annual_inc" : True,"loan_status" : True, "num_sats" : True, "last_pymnt_amnt" : True,
        "avg_cur_bal" : True, "addr_state" : True }) 
    json_projects = []
    for project in projects:
        json_projects.append(project)
    json_projects = json.dumps(json_projects, default=json_util.default)
    return json_projects

@app.route('/eligibility', methods=['POST'])
def predictEligibility():
    funded_amnt = request.form['funded_amnt']
    emp_length = request.form['emp_length']
    avg_cur_bal = request.form['avg_cur_bal']
    num_sats = request.form['num_sats']
    num_actv_rev_tl = request.form['num_actv_rev_tl']
    installment = request.form['installment']
    bc_util = request.form['bc_util']
    total_acc = request.form['total_acc']
    to_predict_list = [funded_amnt, emp_length, avg_cur_bal, num_actv_rev_tl,  num_sats, installment, bc_util, total_acc]
    with open('RFM.pkl','rb') as f:
        loaded_model =  pickle.load(f)
    result = loaded_model.predict([to_predict_list]) 
    if result[0] == 1:
        return render_template('eligibility.html', output ='Accepted.')
        # return jsonify({'output': 'accepted!'})
    else: 
        return render_template('eligibility.html', output ='Rejected.')
        # return jsonify({'output3': 'rejected!'})

@app.route('/InterestRate', methods=['POST'])
def predictInterestRate():
    funded_amnt = request.form['funded_amnt']
    emp_length = request.form['emp_length']
    annual_inc = request.form['annual_inc']

    to_predict_list = [[funded_amnt, emp_length, annual_inc]]
    polynomial_features = PolynomialFeatures(degree=3)
    to_predict_list = polynomial_features.fit_transform(to_predict_list)
    with open('IntRateRegression.pkl','rb') as f:
        loaded_model = model#pickle.load(f)
    result = loaded_model.predict(to_predict_list)    
    return jsonify({'output': str(float("{0:.2f}".format(result[0]))) + '%'})

@app.route('/addLoan', methods=['POST'])
def predictEligibilityAndInterestRate():
    funded_amnt = request.form['funded_amnt']
    emp_length = request.form['emp_length']
    avg_cur_bal = request.form['avg_cur_bal']
    num_sats = request.form['num_sats']
    num_actv_rev_tl = request.form['num_actv_rev_tl']
    installment = request.form['installment']
    bc_util = request.form['bc_util']
    total_acc = request.form['total_acc']
    annual_inc = request.form['annual_inc']

    to_predict_list1 = [funded_amnt, emp_length, avg_cur_bal, num_actv_rev_tl,  num_sats, installment, bc_util, total_acc]
    to_predict_list2 = [[funded_amnt, emp_length, annual_inc]]
    polynomial_features = PolynomialFeatures(degree=3)
    to_predict_list2 = polynomial_features.fit_transform(to_predict_list2)
    with open('RFM.pkl','rb') as f1:
        loaded_model1 =  pickle.load(f1)
    with open('IntRateRegression.pkl','rb') as f2:
        loaded_model2 =  pickle.load(f2)
    result1 = loaded_model1.predict([to_predict_list1])
    result2 = loaded_model2.predict(to_predict_list2) 
    
    if result1[0] == 1:
        return jsonify({
            'output': 'accepted!',
            'output1': 'The interest rate should be around ',
            'output2': str(float("{0:.2f}".format(result2[0]))) + '%'})
    else: 
        return jsonify({'output3': 'rejected!'})

    
if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host="127.0.0.1",port=8080,debug=True)

def api_response():
    from flask import jsonify
    if request.method == 'POST':
        return jsonify(**request.json)   
