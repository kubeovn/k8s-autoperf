import os
from subprocess import PIPE, Popen


def gen_yaml_para(input):
    return str(input)


def gen_svg():
    names = [name for name in os.listdir("./result")
             if (os.path.isfile(os.path.join('./result', name)) and name.endswith('.data'))]
    if len(names) == 0:
        return
    for name in names:
        fname = name.split(".data")[0]
        file = "./result/" + name
        out = "./result/" + fname + ".out"
        print(file, out)
        process = Popen(['perf', 'script', '-i', file, '>', out], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        print(eval(stdout.decode('utf-8')), eval(stderr.decode('utf-8')))
        fold = "./result/" + fname + ".fold"
        process = Popen(['FlameGraph/stackcollapse-perf.pl', out, '>', fold], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        print(eval(stdout.decode('utf-8')), eval(stderr.decode('utf-8')))
        svg = "./result/" + fname + ".svg"
        process = Popen(['FlameGraph/flamegraph.pl', fold, '>', svg], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        print(eval(stdout.decode('utf-8')), eval(stderr.decode('utf-8')))
        process = Popen(['yes', '|', 'rm', fold, out], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        print(eval(stdout.decode('utf-8')), eval(stderr.decode('utf-8')))
