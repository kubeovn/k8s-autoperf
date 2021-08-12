import datetime
import os
import socket
from subprocess import Popen, PIPE
from time import sleep
from threading import Thread


SETTIME = os.environ["TIME"]
DURATION = os.getenv("DURATION", "null")
if DURATION == "null":
    DURATION = 60
PERF = "perf"
STEP = os.getenv("STEP", "null")
if STEP == "null":
    STEP = 5


def record_top(duration):
    HOST = socket.gethostname()
    i = 1
    while STEP*i <= int(duration):
        with open("/result/" + HOST + "-" + PERF + '-' + SETTIME, "a+") as out, \
                open("/result/" + HOST + "-" + PERF + '-' + SETTIME, "a+") as err:
            process = Popen(['mpstat', '-P', 'ALL'], stdout=out, stderr=err)
            process.wait()
        with open("/result/" + HOST + "-" + PERF + '-' + SETTIME, "a+") as out, \
                open("/result/" + HOST + "-" + PERF + '-' + SETTIME, "a+") as err:
            process = Popen(['top', '-n', '1'], stdout=out, stderr=err)
            process.wait()
        i += 1


floortime = datetime.datetime.strptime(SETTIME, "%H:%M:%S")
uppertime = floortime + datetime.timedelta(days=0, seconds=1)

print("start at %s with due %s" % (datetime.datetime.now().time(), floortime.time()))

while True:
    if floortime.time() <= datetime.datetime.now().time() <= uppertime.time():
        t = Thread(target=record_top, args=(DURATION,))
        t.start()
        process = Popen([PERF, 'record', '-F', '297', '-a', '-g', '-o', '/result/perf.data', '--', 'sleep', '61'],
                        stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print(stderr.decode('utf-8'))
        break
    sleep(1)

sleep(600)
