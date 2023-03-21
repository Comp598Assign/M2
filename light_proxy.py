import subprocess
import docker
from flask import Flask, jsonify, request
import os.path
app = Flask(__name__)
global_list = []
nodes = []
pods={}
jobs =[]
containers=[]
resource_manager_url=''
client = docker.from_env()
client.images.pull('ubuntu')
port = '15000'

class Pod:
    def __init__(self, id):
        self.id = id
        self.pod_nodes = {}
        pods[id] = self

    def __str__(self):
        return self.id
    
class Node:
    idCounter = 0
    def __init__(self, name, parentPod, port):
        self.name = name
        self.status = 'NEW'
        self.port = port
        self.parent = parentPod
        self.id = Node.idCounter
        self.container = None
        parentPod.pod_nodes[name] = self

    def __str__(self):
        return self.name
    
def get_pod(podId):
    if podId in pods:
        return pods[podId]
    return None

def rm_pod(pod):
    pods.pop(pod.id)

def rm_node(node):
    node.parent.pod_nodes.pop(node.name)
    nodes.remove(node)
    if node.container is not None:
        node.container.remove(v=True, force=True)

def get_node(node_name):
    for node in nodes:
        if node.name == node_name:
            return node
    return None

def get_available_port():
    global port
    p = port
    port = str(int(port) + 1)
    return p


@app.route('/cloudproxy/initalization')
def cloud_init():
    if request.method == "GET":  
        light_pod = Pod("light_pod")
        # medium_pod = Pod("medium_pod")
        # heavy_pod = Pod("heavy_pod")

        #get rm ip
        # headers_list = request.headers.getlist("X-Forwarded-For")
        # ip = headers_list[0] if headers_list else request.remote_addr
        # global resource_manager_url
        # resource_manager_url = 'http://'+ip+':5000'
        #

        return jsonify({"response" : 'success'})

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

@app.route('/cloudproxy/allPods', methods = ['GET'])
def pod_register(pod_name):
    if request.method == "GET":
        response = {}
        for pod in pods:
            response[pod.id] = [len(pod.pod_nodes)]
        return jsonify(response)



@app.route('/cloudproxy/<podId>/nodes/<name>', methods = ['POST'])
def node_register(podId, name):
    
    if request.method == "POST":
        if len(nodes) >= 20:
            result = 'Pod capacity has been reached (max 20 nodes)'
            return jsonify({"result" : result})
        
        for node in nodes:
            if node.name == name:
                result = 'node with the same already exists'
                return jsonify({"result" : result})
            
        # container = client.containers.run('ubuntu', name = name, detach = True, tty = True)
        nodes.append(Node(name, get_pod(podId), get_available_port()))
        result = 'Added NEW node under ' + podId 
        return jsonify({"result" : result})
               

@app.route('/cloudproxy/nodes/<node_name>', methods = ['DELETE'])
def node_rm(node_name):
    node = get_node(node_name)
    if node is None:
        return jsonify({"response" : "failure", "msg" : "node does not exist."})
    rm_node(node)
    return jsonify({"response" : "success", "name" : node.name, "port" : node.port, "status" : node.status}) 
    # change response msg for other proxies



@app.route('/cloudproxy/<podId>/allNodes', methods = ['GET'])
def nodes_list(podId):
    result={}
    if podId == "allPods":
        for node in nodes:
            result[node.name]=[str(node.id), node.status]
    else:
        pod = get_pod(podId)
        if pod is not None:
            for node in pod.pod_nodes.values():
                result[node.name]=[str(node.id), node.status]
        else:
            result = "failure"

    return jsonify({'response' : result})


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


@app.route('/cloudproxy/launch', methods = ['GET'])
def launch():
    if request.method == 'GET':
        for node in nodes:
            if node.status == "NEW":
                launch_node(node.name, node.port)
                return jsonify ({'response' : 'success' ,'port' : node.port, 'name' : node.name, 'status' : node.status})
        return jsonify({'response ' : 'failure', 'result' : 'No more available nodes'})


def launch_node(container_name, port_number):
    # [img, logs] = client.images.build (path='/', rm=True ,dockerfile = './Dockerfile' )

    for container in client.containers.list():
        if container.name == container_name:
            container.remove(v=True, force=True)

    [img, logs] = client.images.build (path='./', rm=True ,dockerfile = './Dockerfile' )
    # for container in client.containers.list():
    #     if container.name == container_name :
    #         container.remove(v=True, force=True)
    container = client.containers.run(image=img, detach=True, name=container_name, command=['python' , 'app.py', container_name],ports={'5000/tcp' : port_number}, tty=True)
    # container = client.containers.run(image='ubuntu', detach=True, name=container_name, command=['echo', 'hello', 'world'],ports={'5000/tcp' : port_number})
    node = get_node(container_name)
    node.container = container
    node.status = "ONLINE"

    # msg = ('Successfully launched node: %s under light pod on port %s' % (node.name, node.port))
    
    # index = -1
    # for i in range(len(nodes)):
    #     node = nodes[i]
    #     if container_name == node['name']:
    #         index = i
    #         nodes[i] = { 'port ' : port_number,'name ': container_name,'running': True}
    #         break




if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port=5000)