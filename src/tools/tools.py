import os
from subprocess import PIPE, Popen
import ipaddress


def get_pod_ip():
    process = Popen(['kubectl', '-n', 'kube-system', 'get', 'pod', '-l', 'app=kubeovn-perfserver', '-o',
                     "jsonpath='{.items[*].status.podIP}'"],
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    rslts = eval(stdout.decode('utf-8')).split("\n")
    ipaddress.ip_address(rslts[0])
    return rslts[0]


def get_svc_ip():
    process = Popen(['kubectl', '-n', 'kube-system', 'get', 'svc', '-l', 'app=kubeovn-perfserver', '-o',
                     "jsonpath='{.items[*].spec.clusterIP}'"],
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    rslts = eval(stdout.decode('utf-8')).split("\n")
    ipaddress.ip_address(rslts[0])
    return rslts[0]


def check_value(lists, value):
    for i in lists:
        if i != value:
            return False
    return True


def gen_yaml_para(input):
    return str(input)


def gen_svg():
    names = [name for name in os.listdir("./result")
             if (os.path.isfile(os.path.join('./result', name)) and name.endswith('.data'))]
    if len(names) == 0:
        return
    for name in names:
        print(name)
        fname = name.split(".data")[0]
        file = "./result/" + name
        out = "./result/" + fname + ".out"
        with open(out, "w+") as sout, open(out, "w+") as err:
            process1 = Popen(['perf', 'script', '-i', file], stdout=sout, stderr=err)
            process1.wait()
        fold = "./result/" + fname + ".fold"
        print("generate: ", out)
        with open(fold, "w+") as sout, open(fold, "w+") as err:
            process1 = Popen(['FlameGraph/stackcollapse-perf.pl', out], stdout=sout, stderr=err)
            process1.wait()
        svg = "./result/" + fname + ".svg"
        print("generate", fold)
        with open(svg, "w+") as sout, open(svg, "w+") as err:
            process1 = Popen(['FlameGraph/flamegraph.pl', fold], stdout=sout, stderr=err)
            process1.wait()
        print("generate: ", svg)
        process = Popen(['rm', '-f', fold, out], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        print(stdout.decode('utf-8'), stderr.decode('utf-8'))
