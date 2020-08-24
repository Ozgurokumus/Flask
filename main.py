from flask import Flask, render_template, url_for, request, redirect, session
from urllib.request import urlopen
from datetime import datetime
from functools import wraps
from variables import mode
import pandas as pd 
import requests
import json
import time
import csv


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

@app.route("/")
@app.route("/home", methods =["GET"])
def home():
    ip = str(request.remote_addr)
    unix_time = round(time.time())
    browser = request.user_agent.browser
    platform = request.user_agent.platform
    if ip == '':
        url = 'https://ipinfo.io/json'
    else:
        url = 'https://ipinfo.io/' + ip + '/json'
    res = urlopen(url)
    data = json.load(res)
    try:
        city = data['city']
    except:
        city = 'Unknown'

    date = datetime.utcfromtimestamp(unix_time+10800).strftime('%Y-%m-%d %H:%M:%S')
    with open("logs.txt","a") as f: 
        f.write(str({"ip":ip, "City":city, "Unix time":unix_time, "Browser":browser, "Platform":platform, "Date":date})+"\n")

    return render_template('home.html')

@app.route("/exchange")
def exchange():
    uri = "https://api.exchangeratesapi.io/latest"
    try:
        uResponse = requests.get(uri)
    except requests.ConnectionError:
       return "Connection Error"  
    Jresponse = uResponse.text
    data = json.loads(Jresponse)

    rates = data['rates'] # Rates dictionary
    tr = rates['TRY']
    for k,v in rates.items(): rates[k] = round(tr/v,4)
    tr = round(tr,4)
    last_update = data['date'] # Last update date

    return render_template('exchange.html', title='Exchange', rates = rates, last_update = last_update, tr = tr)
    
@app.route("/dictionary_optional")
def dictionary_optional():
    data = pd.read_csv("static\dictionary.csv")
    return render_template('dictionary_optional.html', title='Dictionary-Optional', data = data)

@app.route("/dictionary", methods=['GET','POST'])
def dictionary():
    global mode 

    with open('static\dictionary.csv', mode='r', encoding="utf8") as f:
        csvFile = csv.reader(f)
        trToEng = {rows[0].lower():rows[1].lower() for rows in csvFile}
        engToTr = {value:key for key, value in trToEng.items()}

    if request.method == 'POST':
        if 'switch' in request.form:
            mode*= -1
            print(mode)
            return render_template('dictionary.html', title='Dictionary', mode = mode)

        elif 'translate' in request.form and mode == 1:
            if request.form['translate'].lower() in trToEng:
                return render_template('dictionary.html', title='Dictionary', translate = trToEng[request.form['translate'].lower()], mode = mode)
            else:
                return render_template('dictionary.html', title='Dictionary', notFound = True, mode = mode)

        elif 'translate' in request.form and mode == -1:
            if request.form['translate'].lower() in engToTr:
                return render_template('dictionary.html', title='Dictionary', translate = engToTr[request.form['translate'].lower()], mode = mode)
            else:
                return render_template('dictionary.html', title='Dictionary', notFound = True, mode = mode)

    return render_template('dictionary.html', title='Dictionary', mode = mode)

@app.route("/logs")
@login_required
def logs():
    with open("logs.txt","r") as f:
        logs = f.readlines()
    for i in range(len(logs)): logs[i] = eval(logs[i])

    return render_template('logs.html', title='Logs', logs = logs)

@app.route("/login", methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['password'] != 'q.q':
            error = 'Wrong password, try again.'
        else:
            session['logged_in'] = True
            return redirect(url_for('logs'))
    return render_template('login.html', error=error, title = 'Login')

@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)