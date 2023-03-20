import pycurl
import sys
import requests
from flask import Flask, jsonify, request
import os.path
from urllib.parse import urlencode


def cloud_init(url): #initalize default cluster
    r = requests.get(url + '/cloud/initalization')
    print(r.text)
    

def cloud_register_node(url, node_name, pod_id): #TODO specify pod type in request
    r = requests.post(url + '/cloud/' + str(pod_id) + '/nodes/' + node_name)
    print(r.text)

def cloud_remove_node(url, node_name, pod_id): #dispatch request to appropriate pod
    r = requests.delete(url + '/cloud/' + pod_id + '/rm/' + node_name)
    print(r.text)

def cloud_launch_job_with_path(url, file_path):
    if os.path.isfile(file_path):
        files = {'file':open(file_path,'rb')}
        ret = requests.post(url+'/cloud/jobs',files =files)
        if ret.ok:
            print("ok")
        else :
            print("error")

def cloud_abort_job(url, job_id):
    #todo
    return 0

def cloud_launch_pod(url, pod_id):
    #launch pod
    r = requests.get(url + '/cloud/' + pod_id + '/launch')
    print(r.text)
    return 0

def cloud_resume_pod(url, pod_id):
    #resume pod
    #If there are any nodes with the “ONLINE” status, then the Load Balancer should include these in its configuration so that it can start sending traffic through to this node again.
    return 0

def cloud_pause_pod(url, pod_id):
    #All the nodes with the “ONLINE” status inside this pod are removed and the Load Balancer is notified so that no more incoming client request on this pod will receive a response
    return 0

def  cloud_pod_ls(url):
    response = requests.get(url + '/cloud/allPods')
    data = response.json()
    for pod_id, node_number in data:
        print("pod_id: %s has %d nodes" % (pod_id, node_number))
    
def cloud_node_ls(url, pod_id='allPods'):
    response = requests.get(url + '/cloud/' + pod_id + '/nodes/all')
    data = response.json()
    for k, v in data["response"].items():
        print("node: %s; id: %s; status: %s" % (k, v[0], v[1]))

def main():
    rm_url = sys.argv[1]
    cloud_init(rm_url)
    while (1):
        command = input('$ ')
        commandstr = command.split()
        if command == 'cloud init': #TODO: init three pod
            cloud_init(rm_url)
        elif command.startswith('cloud register') and len(commandstr)==4:
            cloud_register_node(rm_url,commandstr[2],commandstr[3])
        elif command.startswith('cloud rm') and len(commandstr)==4:
            cloud_remove_node(rm_url,commandstr[2],commandstr[3])
        elif command.startswith('cloud launch') and len(commandstr)==3:
            #launch pod
            cloud_launch_job_with_path(rm_url,commandstr[2])
        elif command.startswith('cloud resume') and len(commandstr)==3:
            cloud_resume_pod(rm_url,commandstr[2])
        elif command.startswith('cloud pause') and len(commandstr)==3:
            cloud_pause_pod(rm_url,commandstr[2])
        elif command.startswith('cloud abort') and len(commandstr)==3:
            cloud_abort_job(rm_url,commandstr[2])
        elif command == 'cloud pod ls':
            cloud_pod_ls(rm_url)
        elif command.startswith('cloud node ls') and len(commandstr)==3:
            cloud_node_ls(rm_url)
        elif command.startswith('cloud node ls') and len(commandstr)==4:
            cloud_node_ls(rm_url, commandstr[3])

if __name__ == '__main__':
    main()