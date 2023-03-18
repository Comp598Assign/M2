import pycurl
import sys
import requests
from flask import Flask, jsonify, request
import os.path
from urllib.parse import urlencode
cURL = pycurl.Curl()

def cloud_hello(url):
    cURL = pycurl.Curl()
    cURL.setopt(cURL.URL, url)
    cURL.perform()
    cURL.close()

def cloud_init(url): #initalize default cluster
    cURL = pycurl.Curl()
    cURL.setopt(cURL.URL, url + '/cloud/clusters/initalization')
    cURL.perform()
    cURL.close()

def cloud_all_clasters(url): #show all clusters
    cURL.setopt(cURL.URL, url + '/cloud/clusters')
    cURL.perform()
    
def cloud_pod_register(url, pod_name): #to created a pod in default cluster
    cURL = pycurl.Curl()
    cURL.setopt(cURL.URL, url + '/cloud/clusters/default_cluster/' + pod_name)
    cURL.setopt(cURL.POST, 1)
    cURL.setopt(cURL.POSTFIELDSIZE, 0)
    cURL.perform()
    cURL.close()
    
def cloud_pod_delete(url, pod_name): #to delete a pod in default cluster
    cURL = pycurl.Curl()
    cURL.setopt(cURL.URL, url + '/cloud/clusters/default_cluster/' + pod_name)
    cURL.setopt(cURL.CUSTOMREQUEST, "DELETE")
    #cURL.setopt(cURL.POSTFIELDSIZE, 0)
    cURL.perform()
    cURL.close()

def num_pods_default(url):
    cURL = pycurl.Curl()
    cURL.setopt(cURL.URL, url + '/cloud/clusters/default_cluster')
    cURL.perform()
    cURL.close()

#===============================================================================
def cloud_register_node(url, node_name, pod_id=-1):
    cURL = pycurl.Curl()
    cURL.setopt(cURL.URL, url + '/cloud/' + str(pod_id) + '/nodes')
    cURL.setopt(cURL.POST, 1)
    data = {'node_name' : node_name, 'pod_id' : pod_id}
    data = urlencode(data)
    cURL.setopt(cURL.POSTFIELDS, data)
    cURL.perform()
    cURL.close()

def cloud_remove_node(url,node_name):
    cURL = pycurl.Curl()
    cURL.setopt(cURL.URL, url + '/cloud/-1/nodes')
    cURL.setopt(cURL.CUSTOMREQUEST, "DELETE")
    data = {'node_name' : node_name}
    data = urlencode(data)
    cURL.setopt(cURL.POSTFIELDS, data)
    cURL.perform()
    cURL.close()

def cloud_launch_job_with_path(url,file_path):
    if os.path.isfile(file_path):
        files = {'file':open(file_path,'rb')}
        ret = requests.post(url+'/cloud/jobs',files =files)
        if ret.ok:
            print("ok")
        else :
            print("error")
def cloud_abort_job(url,job_id):
    #todo
    return 0

def  cloud_pod_ls(url):
    response = requests.get(url + '/cloud/clusters/default_cluster/default_pod')
    data = response.json()
    for k in data:
        print("pod: %s, id: %s has %d nodes" % (data[k][0], k, data[k][1]))
    

def cloud_node_ls(url, pod_id='allPods'):
    response = requests.get(url + '/cloud/' + pod_id + '/nodes')
    data = response.json()
    for k, v in data["response"].items():
        print("node: %s; id: %s; status: %s" % (k, v[0], v[1]))


def main():
    rm_url = sys.argv[1]
    cloud_init(rm_url)
    while (1):
        command = input('$ ')
        commandstr = command.split()
        if command == 'cloud hello':
            cloud_hello(rm_url)
        elif command == 'cloud init':
            cloud_init(rm_url)
        elif command == 'all clusters':
            cloud_all_clasters(rm_url)
        elif command.startswith('cloud pod register') and len(commandstr)==4:
            cloud_pod_register(rm_url, commandstr[3])
        elif command.startswith('cloud pod rm') and len(commandstr)==4:
            cloud_pod_delete(rm_url, commandstr[3])
        elif command.startswith('cloud register') and len(commandstr)==3:
            cloud_register_node(rm_url,commandstr[2])
        elif command.startswith('cloud register') and len(commandstr)==4:
            cloud_register_node(rm_url,commandstr[2],commandstr[3])
        elif command == 'num pods default':
            num_pods_default(rm_url)
        elif command.startswith('cloud rm') and len(commandstr)==3:
            cloud_remove_node(rm_url,commandstr[2])
        elif command.startswith('cloud launch') and len(commandstr)==3:
            cloud_launch_job_with_path(rm_url,commandstr[2])
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
    