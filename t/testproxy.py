from flask import Flask, jsonify , request
import sys
import docker
import subprocess
app = Flask(__name__)
client = docker.from_env()
client.images.pull('ubuntu')
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
    node_list.append({'port' : port, 'name' : name , 'running' : False}) 
    print(node_list)
    return jsonify({ 'response' : 'success ',
        'port' : port,
        'name' : name,
        'running' : False})



@app.route('/launch')
def launch():
    for node in node_list:
        if not node['running']:
            a = launch_node(node['name'], node['port'])
        if node is not None:
            return jsonify ({'response' : 'success' ,
                             'port' : node['port'], 
                             'name' : node['name'],
                             'running' : "yes"})
    return jsonify({'response ' : 'failure', 'reason' : 'Unknown reason'})


def launch_node(container_name, port_number):

    container = client.containers.run('ubuntu', name = container_name, detach = True, tty = True, ports={'5000/tcp' : port_number})

    subprocess.Popen(['docker','exec',container.id,'bash','-c', "echo good"])

    print('Succesfully launched a node' )
    return 0
if __name__== '__main__' :
    app. run(debug=True,host='0.0.0.0', port=5000)
