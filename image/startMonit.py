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
STEP = os.getenv("STEP", "null")
if STEP == "null":
    STEP = 5
else:
    STEP = int(STEP)
PERF = "perf"
HOST = socket.gethostname()


def record_top(duration):
    i = 1
    while STEP*i <= int(duration):
        with open("/result/" + HOST + "-" + PERF + '-' + SETTIME + "cpu", "a+") as out, \
                open("/result/" + HOST + "-" + PERF + '-' + SETTIME + "cpu", "a+") as err:
            process1 = Popen(['mpstat', '-P', 'ALL'], stdout=out, stderr=err)
            process1.wait()
        with open("/result/" + HOST + "-" + PERF + '-' + SETTIME + "top", "a+") as out, \
                open("/result/" + HOST + "-" + PERF + '-' + SETTIME + "top", "a+") as err:
            process2 = Popen(['top', '-b', '-n', '1'], stdout=out, stderr=err)
            process2.wait()
        i += 1


floortime = datetime.datetime.strptime(SETTIME, "%H:%M:%S")
uppertime = floortime + datetime.timedelta(days=0, seconds=1)

print("start at %s with due %s" % (datetime.datetime.now().time(), floortime.time()))

while True:
    if floortime.time() <= datetime.datetime.now().time() <= uppertime.time():
        t = Thread(target=record_top, args=(DURATION,))
        t.start()
        dst = "/result/" + HOST + '-' + SETTIME + '-' + "perf.data"
        process = Popen([PERF, 'record', '-F', '297', '-a', '-g', '-o', dst, '--', 'sleep', '61'],
                        stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print(stderr.decode('utf-8'))
        break
    sleep(1)

sleep(600)
