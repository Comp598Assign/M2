from io import BytesIO
from flask import Flask, jsonify, request, render_template
import pycurl
import sys
import json
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv
load_dotenv()
import os

app = Flask(__name__)
proxy_url = os.environ.get("ip")
cURL = pycurl.Curl()

jobs =[]
jobidcounter_fornextjob =0
class Job:
    def __init__(self,status,file,pNode = None):
        global jobidcounter_fornextjob 
        self.id = jobidcounter_fornextjob
        self.status = status
        self.file = file
        self.node_running_on = pNode
        jobidcounter_fornextjob+=1
    def __str__(self):
        if self.node_running_on == None:
            return "Registerd Job waiting in Queque"
        else:
            return "Job id:"+self.id +"running in Node: " + self.node_running_on
    
def get_av_node():
    response = requests.get(proxy_url+'/cloudproxy/get_nextav_node')
    data = response.json()
    return data["av_node"]

@app.route('/dashboard')
def dashboard():
    response = requests.get(proxy_url + '/cloudproxy/allPods/nodes/all')
    data = response.json()
    print(data)
    return render_template("Dashboard.html", data=data['result'])


@app.route('/hello', methods = ['GET', 'POST'])
def cloud():
    if request.method == "GET":
        print("A Client says hello")
        response = "Cloud says hello"
        return jsonify({"response" : response})

@app.route('/cloud/clusters/initalization') #initalize default cluster
def cloud_init():
    response = requests.get(proxy_url + '/cloudproxy/default_cluster/initalization')
    data = response.json()
    response = data["response"]
    return jsonify({"response" : response})

@app.route('/cloud/clusters/default_cluster/<pod_name>', methods = ['POST', 'DELETE', 'GET']) #rigster new pod
def cloud_pod_registration_remove(pod_name):
    if request.method == "POST":
        response = requests.post(proxy_url + '/cloudproxy/default_cluster/' + pod_name)
        data = response.json()
        s = data["result"]
        return jsonify({"response" : s})
    
    elif request.method == "DELETE":
        response = requests.delete(proxy_url + '/cloudproxy/default_cluster/' + pod_name)
        data = response.json()
        return jsonify({'response' : data['result']})

    elif request.method == "GET":
        response = requests.get(proxy_url + '/cloudproxy/default_cluster/' + pod_name)
        data = response.json()
        return jsonify(data)

#@app.route('/cloud/nodes/<name>', defaults={'pod_name': 'default'}, methods = ['POST', 'DELETE'])
@app.route('/cloud/<pod_id>/nodes', methods = ['POST', 'DELETE', 'GET'])
def cloud_register_delete_node(pod_id):
    if request.method == "POST":
        response = requests.post(proxy_url + '/cloudproxy/' + pod_id + '/nodes/' + request.form['node_name'])
        data = response.json()
        response = data['node_status'] + ' node named ' + request.form['node_name'] + ' ' + data['result'] + ' under pod ' + str(data['pod_id'])
        return jsonify({"response" : response})

    elif request.method == "DELETE":
        response = requests.delete(proxy_url + '/cloudproxy/nodes/' + request.form['node_name'])
        data = response.json()
        return jsonify({"response" : data['response']})
        
    elif request.method == "GET":
        response = requests.get(proxy_url + '/cloudproxy/' + pod_id + '/nodes/all')
        data = response.json()
        return jsonify({"response" : data['result']})


@app.route('/cloud/jobs',methods=['POST'])
def cloud_launch():
    if request.method == 'POST':
        print("request to post file")
        jobf = request.files['file']
        #
        next_node = get_av_node()
        if next_node == None:
            job = Job("Registered",jobf)
            jobs.append(job)
        else:
            job = Job("Running",jobf,next_node)
            response = requests.post(proxy_url+'/cloudproxy/jobs/'+str(job.id)+'/'+next_node,files ={'file':jobf})
            data = response.json()
            response =data["response"]
            print(response)
            return jsonify({"response" : response})
        

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port=5000)