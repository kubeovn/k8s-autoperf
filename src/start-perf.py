import datetime
import time
from subprocess import Popen, PIPE
import ipaddress
import yaml

DSTDIR = './result/'


def nodesCheck():
    process = Popen(['kubectl', 'get', 'nodes', '-l', 'perf-role=client', '-o', 'name'],
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    rslts = stdout.decode('utf-8').split("\n")
    if len(rslts) != 2:
        raise Exception("client node are not labeled")

    process = Popen(['kubectl', 'get', 'nodes', '-l', 'perf-role=server', '-o', 'name'],
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    rslts = stdout.decode('utf-8').split("\n")
    if len(rslts) != 2:
        raise Exception("client node are not labeled")


def deploy_monitor(starttime, podip):
    with open('./templates/kubeovn-perfmonitor.yaml', 'r') as f:
        yml_doc = yaml.safe_load(f)
        if yml_doc is None:
            raise Exception("template monitor not right")
        alist = yml_doc['spec']['template']['spec']['containers'][0]['env']
        for i in range(len(alist)):
            if alist[i]['name'] == 'SERVER':
                yml_doc['spec']['template']['spec']['containers'][0]['env'][i]['value'] = podip
            if alist[i]['name'] == 'TIME':
                yml_doc['spec']['template']['spec']['containers'][0]['env'][i]['value'] = starttime.strftime("%H:%M:%S")
        with open('/tmp/kubeovn-perfclient.yaml', 'w+') as tf:
            yaml.dump(data=yml_doc, stream=tf, allow_unicode=True)

    process = Popen(['kubectl', 'create', '-f', '/tmp/kubeovn-perfmonitor.yaml'],
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode('utf-8'), stderr.decode('utf-8'))


def deploy_client(starttime, podip):
    with open('./templates/kubeovn-perfclient.yaml', 'r') as f:
        yml_doc = yaml.safe_load(f)
        if yml_doc is None:
            raise Exception("template client not right")
        alist = yml_doc['spec']['template']['spec']['containers'][0]['env']
        for i in range(len(alist)):
            if alist[i]['name'] == 'SERVER':
                yml_doc['spec']['template']['spec']['containers'][0]['env'][i]['value'] = podip
            if alist[i]['name'] == 'TIME':
                yml_doc['spec']['template']['spec']['containers'][0]['env'][i]['value'] = starttime.strftime("%H:%M:%S")
        with open('/tmp/kubeovn-perfclient.yaml', 'w+') as tf:
            yaml.dump(data=yml_doc, stream=tf, allow_unicode=True)

    process = Popen(['kubectl', 'create', '-f', '/tmp/kubeovn-perfclient.yaml'],
                stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode('utf-8'), stderr.decode('utf-8'))


def retrieve_data(label):
    process = Popen(['kubectl', '-n', 'kube-system', 'get', 'pod', '-l',
                     label, '-o', "jsonpath='{..metadata.namespace}/{..metadata.name}'"],
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    rslts = stdout.decode('utf-8').split("\n")
    srcpod = eval(rslts[0])
    srcdir = srcpod + ':/result'
    process = Popen(['kubectl', 'cp', srcdir, DSTDIR], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode('utf-8'), stderr.decode('utf-8'))


def delete_dep():
    process = Popen(['kubectl', '-n', 'kube-system', 'delete', 'deploy',
                     'kubeovn-perfclient', 'kubeovn-perfserver', 'kubeovn-perfmonitor'],
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode('utf-8'), stderr.decode('utf-8'))


nodesCheck()

process = Popen(['kubectl', 'create', '-f', './templates/kubeovn-perfserver.yaml'],
                stdout=PIPE, stderr=PIPE)
stdout, stderr = process.communicate()
print(stdout.decode('utf-8'), stderr.decode('utf-8'))

while True:
    process = Popen(['kubectl', '-n', 'kube-system', 'get', 'pod', '-l', 'app=kubeovn-perfserver', '-o',
                     "jsonpath='{.items[*].status.containerStatuses[*].ready}'"],
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    rslts = stdout.decode('utf-8').split("\n")
    if len(rslts) == 1 and eval(rslts[0]) == "true":
        print("server is ready")
        break

process = Popen(['kubectl', '-n', 'kube-system', 'get', 'pod', '-l', 'app=kubeovn-perfserver', '-o',
                 "jsonpath='{.items[*].status.podIP}'"],
                stdout=PIPE, stderr=PIPE)
stdout, stderr = process.communicate()
rslts = stdout.decode('utf-8').split("\n")
ipaddress.ip_address(eval(rslts[0]))
podip = eval(rslts[0])

starttime = datetime.datetime.now() + datetime.timedelta(days=0, minutes=2)
nowtime = time.strftime("%H:%M:%S", time.localtime())

deploy_client(starttime, podip)
deploy_monitor(starttime, podip)

while True:
    if starttime.time() <= datetime.datetime.now().time():
        break
    time.sleep(1)
time.sleep(65)

retrieve_data("'app=kubeovn-perfclient'")
retrieve_data("'app=kubeovn-perfmonitor'")
delete_dep()
