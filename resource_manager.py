from io import BytesIO
import subprocess
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

proxy_url['light_pod'] = os.environ.get("light_proxy_ip")
# proxy_url['medium_pod'] = os.environ.get("medium_proxy_ip")
# proxy_url['heavy_pod'] = os.environ.get("heavy_proxy_ip")



jobs =[]
jobidcounter_fornextjob = 0
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
            return "Job id:"+ self.id +"running in Node: " + self.node_running_on
    
def get_av_node():
    response = requests.get(proxy_url+'/cloudproxy/get_nextav_node')
    data = response.json()
    return data["av_node"]

def get_proxy_url_no_port(pod_id):
    return ":".join(proxy_url[pod_id].split(':').pop())


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
        if response.json()["response"] != 'success':
            success = False

    if success:
        result = 'successfully created light, medium and heavy resource pods'
    else: 
        result = 'initialization failed'

    return jsonify({"response" : result})
    

@app.route('/cloud/allPods', methods = ['GET']) #get pod id 
def cloud_pod_get(pod_id):
    if request.method == "GET":
        return requests.get(proxy_url[pod_id] + '/cloudproxy/allPods')
    

#@app.route('/cloud/nodes/<name>', defaults={'pod_name': 'default'}, methods = ['POST', 'DELETE'])
@app.route('/cloud/<pod_id>/nodes/<name>/', methods = ['POST', 'GET'])
def cloud_node(pod_id, name):
    if request.method == "POST":
        response = requests.post(proxy_url[pod_id] + '/cloudproxy/' + pod_id + '/nodes/' + name)
        return response.json()
        
    elif request.method == "GET":
        return requests.get(proxy_url['light_proxy_url'] + '/cloudproxy/' + pod_id + '/allNodes').json()
        

@app.route('/cloud/<pod_id>/rm/<node_name>', methods = ['DELETE'])
def cloud_rm_node(pod_id, name):
    if request.method == "DELETE":
        response = requests.delete(proxy_url[pod_id] + '/cloudproxy/nodes/' + name)
        return response.json()
    

@app.route('/cloud/<pod_id>/launch',methods=['GET'])
def cloud_launch_node(pod_id):
    if request.method == "GET":
        response = requests.get(proxy_url[pod_id] + '/cloudproxy/launch')
        data = response.json
        if data["result"] == 'success':
            cmd = "echo 'experimental-mode on; add server servers/'" + data['name'] + ' ' + get_proxy_url_no_port() + ":" + data["port"] + '| sudo socat stdio /var/run/haproxy.sock'
            subprocess.run(cmd, shell = True, check = True)

            enable_cmd = "echo 'experimental-mode on; set server servers/'" + data['name'] + ' state ready ' + '| sudo socat stdio /var/run/haproxy.sock'
            subprocess.run(enable_cmd, shell = True, check = True)

            msg = ('Successfully launched node: %s under light pod on port %s' % (data['name'], data['port']))
        
        return jsonify({'response' : msg})
    

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
            return response.json()
        

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port=5000)