from datetime import datetime, timedelta
import os
from subprocess import Popen
from time import sleep
import socket

IP = os.environ["SERVER"]
PORT = os.environ["PORT"]
SETTIME = os.environ["TIME"]
MSGLEN = os.getenv("MSGLEN", "null")
if MSGLEN == "null":
    MSGLEN = "1400"
DURATION = os.getenv("DURATION", "null")
if DURATION == "null":
    DURATION = "60"
HOST = socket.gethostname()
SOCKPERF = "sockperf"

floortime = datetime.strptime(SETTIME, "%H:%M:%S")
uppertime = floortime + timedelta(days=0, seconds=1)

print("start at %s with due %s" % (datetime.now().time(), floortime.time()))

while True:
    if floortime.time() <= datetime.now().time() <= uppertime.time():
        with open("/result/"+HOST+"-"+IP+"-"+SOCKPERF+"PT", "wb") as out, \
                open("/result/"+HOST+"-"+IP+"-"+SOCKPERF+"PT"+".err", "wb") as err:
            process = Popen([SOCKPERF, 'tp', '-i', IP, '-p', PORT, '--tcp', '-m', MSGLEN, '-t', DURATION],
                            stdout=out, stderr=err)
            process.wait()
        break
    sleep(1)

print("sockperf passthrough finished")


with open("/result/"+HOST+"-"+IP+"-"+SOCKPERF+"Delay", "wb") as out, \
        open("/result/"+HOST+"-"+IP+"-"+SOCKPERF+"Delay"+".err", "wb") as err:
    process = Popen([SOCKPERF, 'pp', '-i', IP, '-p', PORT, '--tcp', '-m', MSGLEN, '-t', DURATION, '--mps=max'],
                    stdout=out, stderr=err)
    process.wait()
print("sockperf delay finished")

sleep(600)
