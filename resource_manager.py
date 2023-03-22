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
    return proxy_url[pod_id].split(':')[1].strip('/')


@app.route('/dashboard')
def dashboard():
    return render_template("Dashboard.html")

@app.route('/nodes/<pod_id>')
def nodes(pod_id):
    str = requests.get(proxy_url[pod_id] + '/cloudproxy/' + pod_id + '/allNodes')
    print(str.json())
    return json.dumps(str.json())


@app.route('/cloud/initalization')
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
    

@app.route('/cloud/<pod_id>/nodes/<name>/', methods = ['POST', 'GET'])
def cloud_node(pod_id, name):
    if request.method == "POST":
        response = requests.post(proxy_url[pod_id] + '/cloudproxy/' + pod_id + '/nodes/' + name)
        return response.json()


@app.route('/cloud/<pod_id>/rm/<name>', methods = ['DELETE'])
def cloud_rm_node(pod_id, name):
    if request.method == "DELETE":
        response = requests.delete(proxy_url[pod_id] + '/cloudproxy/nodes/' + name)
        data = response.json()

        if data["response"] == "failure":
            return data
        
        elif data["response"] == "success" and data["status"] == "ONLINE":
            disable_cmd = "echo 'experimental-mode on; set server light-servers/" + data['name'] + ' state maint ' + "' | sudo socat stdio /run/haproxy/admin.sock"
            subprocess.run(disable_cmd, shell = True, check = True)
            
            del_cmd = "echo 'experimental-mode on; del server light-servers/" + data['name'] + "' | sudo socat stdio /run/haproxy/admin.sock"
            subprocess.run(del_cmd, shell = True, check = True)
            
            msg = ("Removed node %s running on port %s" % (data['name'], data['port'])) 
            return jsonify({"result" : "success", "response" : msg})
    

@app.route('/cloud/<pod_id>/launch',methods=['GET'])
def cloud_launch_pod(pod_id):
    if request.method == "GET":
        response = requests.get(proxy_url[pod_id] + '/cloudproxy/launch')
        data = response.json()
        if data['response'] == 'success':
            
            add_cmd = "echo 'experimental-mode on; add server light-servers/" + data['name'] + ' ' + get_proxy_url_no_port(pod_id) + ":" + data["port"] + "'| sudo socat stdio /run/haproxy/admin.sock"
            subprocess.run(add_cmd, shell = True, check = True)

            enable_cmd = "echo 'experimental-mode on; set server light-servers/" + data['name'] + ' state ready ' + "' | sudo socat stdio /run/haproxy/admin.sock"
            subprocess.run(enable_cmd, shell = True, check = True)

            msg = ('Successfully launched node: %s under light pod on port %s, status: %s' % (data['name'], data['port'], data['status']))
        
        return jsonify({'response' : msg})
    
    
@app.route('/cloud/<pod_id>/resume',methods=['GET'])
def cloud_resume_pod(pod_id):
    if request.method == "GET":
        response = requests.get(proxy_url[pod_id] + '/cloudproxy/online_nodes')
        data = response.json()
        for name in data['node_list']:
            enable_cmd = "echo 'experimental-mode on; set server light-servers/" + name + ' state ready ' + "' | sudo socat stdio /run/haproxy/admin.sock"
            subprocess.run(enable_cmd, shell = True, check = True)


@app.route('/cloud/<pod_id>/pause',methods=['GET'])
def cloud_pause_pod(pod_id):
    if request.method == "GET":
        response = requests.get(proxy_url[pod_id] + '/cloudproxy/online_nodes')
        data = response.json()
        for name in data['node_list']:
            disable_cmd = "echo 'experimental-mode on; set server light-servers/" + name + ' state maint ' + "' | sudo socat stdio /run/haproxy/admin.sock"
            subprocess.run(disable_cmd, shell = True, check = True)
  

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port=5000)