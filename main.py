from flask import Flask, render_template, url_for, request
from urllib.request import urlopen
from datetime import datetime
import requests
import json
import time


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'


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
    last_update = data['date'] # Last update date

    return render_template('exchange.html', title='Exchange', rates = rates, last_update = last_update)
    
@app.route("/dictionary")
def dictionary():
    return render_template('dictionary.html', title='Dictionary')

@app.route("/logs")
def logs():
    with open("logs.txt","r") as f:
        logs = f.readlines()
    for i in range(len(logs)): logs[i] = eval(logs[i])

    return render_template('logs.html', title='Logs', logs = logs)


if __name__ == '__main__':
    app.run(debug=True)