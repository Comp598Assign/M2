from flask import Flask, jsonify , request
import sys
import docker

client = docker.from_env()
app = Flask(__name__)
node_list = []

@app.route( '/register/<name>/<port>')

def register(name, port):
    for node in node_list:
        print(node['port'])
        print(port)
        if node['port'] == port:
            return jsonify({ ' response ' : 'failure' ,'reason' : 'Port already taken '})
        elif node[ 'name ' ] == name :
            return jsonify({ 'response ' : 'failure ' , 'reason ' :'Name already taken '})
    print(node_list)
    node_list.append( {'port' : port, 'name' : name, 'running' : False})
    return jsonify({ 'response' : 'success ',
        'port' : port,
        'name' : name,
        'running' : False})



@app.route('/launch')
def launch():
    for node in node_list:
        if not node['running']:
            node = launch_node(node['name'], node['port'])
        if node is not None:
            return jsonify ({'response' : 'success' ,'port' : node['port'], 'name' : node['name'], 'running' : node['running']})
    return jsonify({'response ' : 'failure', 'reason' : 'Unknown reason'})


def launch_node(container_name, port_number):
    [img, logs] = client.images.build (path='./', rm=True ,dockerfile = './Dockerfile' )
    # for container in client.containers.list():
    #     if container.name == container_name :
    #         container.remove(v=True, force=True)
    client.containers.run(image=img, detach=True, name=container_name, command=['python' , 'app.py',"/bin/bash", container_name],ports={'5000/tcp' : port_number}, tty=True)
    print(logs)
    index = -1
    for i in range(len(node_list)):
        node = node_list[i]
        if container_name == node['name']:
            index = i
            node_list[i] = { 'port' : port_number,'name': container_name,'running': True}
            break
    print('Succesfully launched a node' )
    return node_list[index]
if __name__== '__main__' :
    app. run(debug=True,host='0.0.0.0', port=5000)
