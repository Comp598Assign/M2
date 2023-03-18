import subprocess
import docker
from flask import Flask, jsonify, request
import os.path
app = Flask(__name__)
global_list = []
nodes = []
pods={}
jobs =[]
resource_clusters = []
containers=[]
resource_manager_url=''
client = docker.from_env()
client.images.pull('ubuntu')

class Cluster:
    def __init__(self, name):
        self.name = name
        self.cluster_pods = {}
        self.cluster_pods_id = {}
    def __str__(self):
        return self.name
class Pod:
    def __init__(self, name, parentCluster):
        self.name = name
        self.id = -1
        self.pod_nodes = {}
        self.parent = parentCluster
        parentCluster.cluster_pods[name] = self
    def __str__(self):
        return self.name
class Node:
    idCounter = 0
    def __init__(self, name, parentPod, container):
        self.name = name
        self.status = 'NEW'
        self.parent = parentPod
        self.id = Node.idCounter
        self.container = container
        parentPod.pod_nodes[name] = self
    def __str__(self):
        return self.name
    
def get_pod(podId):
    if podId in pods:
        return pods[podId]
    return None

def rm_pod(pod):
    pod.parent.cluster_pods.pop(pod.name)
    pods.pop(pod.id)

def rm_node(node):
    node.parent.pod_nodes.pop(node.name)
    nodes.remove(node)
    node.container.remove(v=True, force=True)

def get_node(node_name):
    for node in nodes:
        if node.name == node_name:
            return Node(node)
    return None

@app.route('/cloudproxy/default_cluster/initalization')
def cloud_init():
    if request.method == "GET":  
        default_cluster = Cluster("default_cluster") 
        resource_clusters.append(default_cluster)
        default_pod = Pod("default_pod", default_cluster)
        default_cluster.cluster_pods["default_pod"] = default_pod 
        default_cluster.cluster_pods_id[-1] = default_pod 
        pods['-1'] = default_pod
         
        #get rm ip
        headers_list = request.headers.getlist("X-Forwarded-For")
        ip = headers_list[0] if headers_list else request.remote_addr
        global resource_manager_url
        resource_manager_url = 'http://'+ip+':5000'
        #
        response = "default cluster and default pod created"
        return jsonify({"response" : response})

@app.route('/cloudproxy/get_nextav_node',methods=['GET'])
def cloud_getnext_node():
        if request.method == "GET":
            for node in nodes:
                if node.status == 'NEW':
                    return jsonify({"av_node":node.name})
            return jsonify({"av_node":None})
        
@app.route('/default_cluster/pods', methods = ['GET', 'POST'])
def pod_list():
    if request.method == "POST":
        pod_list = request.form['response_from_manager']
        print(pod_list)
        response = "List of pods printed"
        global_list.append(pod_list)
        test()
        return jsonify({"response" : response})

@app.route('/')
def test():
    return global_list[0]

@app.route('/cloudproxy/default_cluster/<pod_name>', methods = ['GET', 'DELETE', 'POST'])
def pod_register(pod_name):
    if request.method == "POST":
        for pod in pods.values():
            print(pod.name, pod_name)
            if pod.name == pod_name:
                result = 'pod name already exists'
                return jsonify({"result" : result})
        pods[pod_name] = Pod(pod_name, resource_clusters[0])
        result = 'pod added'
        return jsonify({"result" : result})
    elif request.method == "DELETE":
        for pod in pods.values():
            if pod.name == pod_name and not pod.pod_nodes and not pod.name == 'default_pod':
                rm_pod(pod)
                return jsonify({'result' : 'remove successful'})
        return jsonify({'result' : 'remove unsuccessful'})
    
    elif request.method == "GET":
        response={}
        for pod in resource_clusters[0].cluster_pods.values():
            response[pod.id] = [pod.name, len(pod.pod_nodes)]
        return jsonify(response)



@app.route('/cloudproxy/<podId>/nodes/<name>', methods = ['POST'])
def node_register(podId, name):
    if request.method == "POST":
        for node in nodes:
            if node.name == name:
                result = 'already exists'
                print({"result" : result, "node_name" : name, "node_status" : node.status, "pod_name" : node.parent.name, "pod_id" : node.parent.id})
                return jsonify({"result" : result, "node_name" : name, "node_status" : node.status, "pod_name" : node.parent.name, "pod_id" : node.parent.id})

        container = client.containers.run('ubuntu', name = name, detach = True, tty = True)
        # subprocess.call(['docker','exec',container.name,'/bin/bash'])

        nodes.append(Node(name, get_pod(podId), container))
        node_status='NEW'
        pod_name=get_pod(podId).name
        result='added'
        return jsonify({"result" : result, "node_name" : name, "node_status" : node_status, "pod_name" : pod_name, "pod_id" : podId})
               
@app.route('/cloudproxy/nodes/<node_name>', methods = ['DELETE'])
def node_rm(node_name):
    for node in nodes:
        if node_name==node.name and node.status == 'NEW':
            rm_node(node)
            response="Removed node " + node.name + " from pod " + node.parent.name 
            return jsonify({"response" : response})
    response="Remove was unsuccessful"
    return jsonify({"response" : response})


@app.route('/cloudproxy/<podId>/nodes/all', methods = ['GET'])
def nodes_list(podId):
    result={}
    if any(c.isalpha() for c in podId):
        for node in nodes:
            result[node.name]=[str(node.id), node.status]
    else: 
        for node in get_pod(podId).pod_nodes.values():
            result[node.name]=[str(node.id), node.status]

    return jsonify({'result' : result})

@app.route('/cloudproxy/jobs/<job_id>/<next_node>',methods=['POST'])


def cloud_lauch_job(job_id,next_node):
    if request.method == 'POST':
        jobf = request.files['file']
        file_name = next_node+'.log'
        container = client.containers.list()[0]
        with open(file_name,'w') as outfile:
            subprocess.Popen(['docker','exec',container.id,'bash','-c',jobf.read().decode("utf-8")],stdout=outfile)      
        print(job_id+"sucessfully run")
        return jsonify({"response": "sucess"})
    else:
        return jsonify({"response": "fail to launch job"})

    
if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port=5000)