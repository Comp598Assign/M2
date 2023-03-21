import json
import subprocess
import threading
from flask import Flask, jsonify, request
import os.path


for x in range(3):
    with open("test.log",'a') as y:
        aaa = subprocess.Popen(['curl', 'http://192.168.1.10:5000'],stdout=y, stderr=y) # url would be url of resouce manager(different port)
