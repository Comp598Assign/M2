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

proxy_url = {}

proxy_url['light_proxy'] = os.environ.get("light_proxy_ip")
# proxy_url['medium_proxy'] = os.environ.get("medium_proxy_ip")
# proxy_url['heavy_proxy'] = os.environ.get("heavy_proxy_ip")

print(proxy_url)
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


@app.route('/cloud/initalization') #initalize default cluster
def cloud_init():
    success = True
    for url in proxy_url.values():
        response = requests.get(url + '/cloudproxy/initalization')
        if response.json["response"] != 'success':
            success = False

    if success:
        result = 'successfully created light, medium and heavy resource pods'
    else: 
        result = 'initialization failed'

    return jsonify({"response" : result})
    

@app.route('/cloud/allPods', methods = ['GET']) #get pod id 
def cloud_pod_get(pod_id):
    if request.method == "GET":
        return requests.get(proxy_url + '/cloudproxy/allPods')
    

#@app.route('/cloud/nodes/<name>', defaults={'pod_name': 'default'}, methods = ['POST', 'DELETE'])
@app.route('/cloud/<pod_id>/nodes/<node_name>', methods = ['POST', 'GET'])
def cloud_node(pod_id, node_name):
    if request.method == "POST":
        response = requests.post(proxy_url[pod_id] + '/cloudproxy/' + pod_id + '/nodes/' + node_name)
        data = response.json()
        response = data['node_status'] + ' node named ' + node_name + ' ' + data['result'] + ' under pod ' + str(data['pod_id'])
        return jsonify({"response" : response})
        
    elif request.method == "GET":
        return requests.get(proxy_url['light_proxy_url'] + '/cloudproxy/' + pod_id + '/allNodes').json()
        

@app.route('/cloud/rm/<node_name>', methods = ['DELETE'])
def cloud_rm_node(node_name):
    if request.method == "DELETE":
        response = requests.delete(proxy_url + '/cloudproxy/nodes/' + node_name)
        data = response.json()
        return jsonify({"response" : data['response']})


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