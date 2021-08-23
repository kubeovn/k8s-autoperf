import datetime
import time
from subprocess import Popen, PIPE
import ipaddress
import yaml
import argparse
from tools import tools


def nodes_check():
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


def deploy_server(port, protocl):
    with open('./templates/kubeovn-perfserver.yaml', 'r') as f:
        yml_doc = yaml.safe_load(f)
        if yml_doc is None:
            raise Exception("template server not right")
        alist = yml_doc['spec']['template']['spec']['containers'][0]['env']
        for i in range(len(alist)):
            if alist[i]['name'] == 'PORT':
                yml_doc['spec']['template']['spec']['containers'][0]['env'][i]['value'] = tools.gen_yaml_para(port)
            if alist[i]['name'] == 'PROTOCOL':
                yml_doc['spec']['template']['spec']['containers'][0]['env'][i]['value'] = tools.gen_yaml_para(protocl)
        with open('/tmp/kubeovn-perfserver.yaml', 'w+') as tf:
            yaml.dump(data=yml_doc, stream=tf, allow_unicode=True)
    process = Popen(['kubectl', 'create', '-f', '/tmp/kubeovn-perfserver.yaml'],
                stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode('utf-8'), stderr.decode('utf-8'))


def deploy_monitor(starttime, podip, intervals):
    with open('./templates/kubeovn-perfmonitor.yaml', 'r') as f:
        yml_doc = yaml.safe_load(f)
        if yml_doc is None:
            raise Exception("template monitor not right")
        alist = yml_doc['spec']['template']['spec']['containers'][0]['env']
        for i in range(len(alist)):
            if alist[i]['name'] == 'SERVER':
                yml_doc['spec']['template']['spec']['containers'][0]['env'][i]['value'] = tools.gen_yaml_para(podip)
            if alist[i]['name'] == 'TIME':
                yml_doc['spec']['template']['spec']['containers'][0]['env'][i]['value'] = starttime.strftime("%H:%M:%S")
            if alist[i]['name'] == 'STEP':
                yml_doc['spec']['template']['spec']['containers'][0]['env'][i]['value'] = tools.gen_yaml_para(intervals)
        with open('/tmp/kubeovn-perfmonitor.yaml', 'w+') as tf:
            yaml.dump(data=yml_doc, stream=tf, allow_unicode=True)

    process = Popen(['kubectl', 'create', '-f', '/tmp/kubeovn-perfmonitor.yaml'],
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode('utf-8'), stderr.decode('utf-8'))


def deploy_client(starttime, podip, port, duration, msglen, protocol):
    with open('./templates/kubeovn-perfclient.yaml', 'r') as f:
        yml_doc = yaml.safe_load(f)
        if yml_doc is None:
            raise Exception("template client not right")
        alist = yml_doc['spec']['template']['spec']['containers'][0]['env']
        for i in range(len(alist)):
            if alist[i]['name'] == 'SERVER':
                yml_doc['spec']['template']['spec']['containers'][0]['env'][i]['value'] = tools.gen_yaml_para(podip)
            if alist[i]['name'] == 'TIME':
                yml_doc['spec']['template']['spec']['containers'][0]['env'][i]['value'] = starttime.strftime("%H:%M:%S")
            if alist[i]['name'] == 'PORT':
                yml_doc['spec']['template']['spec']['containers'][0]['env'][i]['value'] = tools.gen_yaml_para(port)
            if alist[i]['name'] == 'DURATION':
                yml_doc['spec']['template']['spec']['containers'][0]['env'][i]['value'] = tools.gen_yaml_para(duration)
            if alist[i]['name'] == 'MSGLEN':
                yml_doc['spec']['template']['spec']['containers'][0]['env'][i]['value'] = tools.gen_yaml_para(msglen)
            if alist[i]['name'] == 'PROTOCOL':
                yml_doc['spec']['template']['spec']['containers'][0]['env'][i]['value'] = tools.gen_yaml_para(protocol)
        with open('/tmp/kubeovn-perfclient.yaml', 'w+') as tf:
            yaml.dump(data=yml_doc, stream=tf, allow_unicode=True)

    process = Popen(['kubectl', 'create', '-f', '/tmp/kubeovn-perfclient.yaml'],
                stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode('utf-8'), stderr.decode('utf-8'))


def retrieve_data(label, output):
    process = Popen(['kubectl', '-n', 'kube-system', 'get', 'pod', '-l',
                     label, '-o', "jsonpath='{..metadata.namespace}/{..metadata.name}'"],
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    rslts = stdout.decode('utf-8').split("\n")
    srcpod = eval(rslts[0])
    srcdir = srcpod + ':result'
    process = Popen(['kubectl', 'cp', srcdir, output], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print("retrieve finished", stdout.decode('utf-8'), stderr.decode('utf-8'))


def delete_dep():
    process = Popen(['kubectl', '-n', 'kube-system', 'delete', 'deploy',
                     'kubeovn-perfclient', 'kubeovn-perfserver', 'kubeovn-perfmonitor'],
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode('utf-8'), stderr.decode('utf-8'))


def parse_args():
    parser = argparse.ArgumentParser(description="auto Perf for kubernetes")
    parser.add_argument('--output', help='output folder', type=str, default='./result/')
    parser.add_argument('--duration', help='test duration', type=int, default=60)
    parser.add_argument('--msglen', help='sockperf message length', type=int, default=1400)
    parser.add_argument('--intervals', help='intervals between sampling', type=int, default=5)
    parser.add_argument('--port', help='port for test', type=int, default=11111)
    parser.add_argument('--protocol', help='protocol for test', type=str, default="tcp")
    args = parser.parse_args()
    return args


if __name__ == '__main__':

    args = parse_args()
    output = args.output
    duration = args.duration
    msglen = args.msglen
    intervals = args.intervals
    port = args.port
    protocol = args.protocol

    # check if nodes are labeled
    nodes_check()

    # deploy server
    deploy_server(port, protocol)

    # check if server is ready
    while True:
        process = Popen(['kubectl', '-n', 'kube-system', 'get', 'pod', '-l', 'app=kubeovn-perfserver', '-o',
                         "jsonpath='{.items[*].status.containerStatuses[*].ready}'"],
                        stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        rslts = stdout.decode('utf-8').split("\n")
        if len(rslts) == 1 and eval(rslts[0]) == "true":
            print("server is ready")
            break

    # get server pod ip
    process = Popen(['kubectl', '-n', 'kube-system', 'get', 'pod', '-l', 'app=kubeovn-perfserver', '-o',
                     "jsonpath='{.items[*].status.podIP}'"],
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    rslts = stdout.decode('utf-8').split("\n")
    ipaddress.ip_address(eval(rslts[0]))
    podip = eval(rslts[0])

    # set start time for all pod
    starttime = datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=2)
    # nowtime = time.strftime("%H:%M:%S", time.localtime())

    # deploy client/monitor
    deploy_client(starttime, podip, port, duration, msglen, protocol)
    deploy_monitor(starttime, podip, intervals)

    # waiting util test/monitor over
    while True:
        if starttime.time() <= datetime.datetime.utcnow().time():
            break
        time.sleep(1)
    time.sleep(130)

    # retrive datas
    retrieve_data("app=kubeovn-perfclient", output)
    retrieve_data("app=kubeovn-perfmonitor", output)

    # delete all deploys
    delete_dep()

