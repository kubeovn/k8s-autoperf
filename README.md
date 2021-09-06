## k8s-autoperf

[中文教程](https://github.com/lut777/k8s-autoperf/wiki)

##### What is it?

​		k8s-autoperf is a set of tools for automating network performance testing within a Kubernetes cluster. It can automate server/client pod deployments and network performance testing, and it can monitor host status during testing.

​		Eventually, the results of the above tests and monitoring will be exported as files and flame charts to a local `./result/` folder. The results of each test will be distinguished by the time of the test as a file name.



##### How to use:

​		Installing dependencies (centos for example):

```shell
yum install python3 python3-pip3 perf perl* -y
pip3 install pyyaml
```

​		Identify the node where the perf-client is located by marking the node, `CLIENT-NODE` is the name of the node:

```shell
kubectl label nodes CLIENT-NODE perf-role=client
```

​		Identify the node where the perf-server is located by marking the node, `SERVER-NODE` is the name of the node:

```shell
kubectl label nodes SERVER-NODE perf-role=server
```

​		Mark the nodes that need to be monitored. Multiple nodes can be tagged, for example both the client and server nodes. The cpu/flame map/memory resources of the host will be monitored during testing.

```shell
kubectl label nodes SERVER-NODE perf-monitor=yes
kubectl label nodes CLIENT-NODE perf-monitor=yes
```

​		Go to the `src` directory and start the test, wait for it to complete, and then find the results in the `. /result` directory.

```shell
[root@perf-c3-small-x86-01 src]# python3 ./start-perf.py
deployment.apps/kubeovn-perfserver created
server is ready
deployment.apps/kubeovn-perfclient created
daemonset.apps/kubeovn-perfmonitor created
The test will take a few minutes, please be patient.
retrieve finished
retrieve finished for  kubeovn-perfmonitor-rjzv4
retrieve finished for  kubeovn-perfmonitor-zfkbr
deployment.apps "kubeovn-perfclient" deleted
deployment.apps "kubeovn-perfserver" deleted
daemonset.apps "kubeovn-perfmonitor" deleted
master-10:35:19-perf.data
generate:  ./result/master-10:35:19-perf.out
generate ./result/master-10:35:19-perf.fold
generate:  ./result/master-10:35:19-perf.svg

slave-10:35:19-perf.data
generate:  ./result/slave-10:35:19-perf.out
generate ./result/slave-10:35:19-perf.fold
generate:  ./result/slave-10:35:19-perf.svg

[root@perf-c3-small-x86-01 src]# ls ./result/
kubeovn-perfclient-57ffbdb88b-tqxr6-10.16.0.7-sockperfDelay  master-10:35:19-perf.data  master-perf-10:35:19cpu  slave-10:35:19-perf.data  slave-perf-10:35:19cpu
kubeovn-perfclient-57ffbdb88b-tqxr6-10.16.0.7-sockperfPT     master-10:35:19-perf.svg   master-perf-10:35:19top  slave-10:35:19-perf.svg   slave-perf-10:35:19top
```

​		The delay test results are saved in a file ending in `Delay`, the bandwidth test results are saved in a file ending in `PT` (Passthought), and the flame graph data of test node during the bandwidth test is saved in `perf-TIME-NODE.data`. The generated flame graphs are `svg` files with the same name.  The `cpu` usage is stored in the `perf-NODE-TIMEcpu` file. System usage is saved by the `perf-NODE-TIMEtop` file.



##### Sample use:

1, Testing the network performance of direct connections between pods

```shell
python3 ./start-perf.py
```

2, Tests the network performance with a pod accessing another service in the cluster with the service ip as the destination ip. The number of endpoints can be specified.

```shell
python3 ./start-perf.py --svcport true  --epnumber 2
```

3, Test the network performance with a pod accessing another pod deployed in hostnet mode (or vice versa).

```shell
python3 ./start-perf.py --serverhost true
```



##### Execution process:

​		src/start-pef sets the parameters and start time, and configures a temporary yaml file based on the template (which can be found in the /tmp/ directory and checked for validation). 

​		The temporary yaml file is then deployed to k8s. The client pod starts the test at the start time, the monitor pod monitors it and stores the results in a file.

​		After a certain amount of time, start-perf retrieves the data and removes the test resources. 



##### Execution requirements:

​		1, There must be a node with perf-role=server in its label, which is the server node under test. There must be a different node labeled perf-role=client, which is the client node under test. This requirement will be checked before the test is executed.

​		2, Currently the monitor side is executed as root. If you think there is a security risk, you can also run the following command on the node where the monitor is to be deployed in advance. 

​			`echo "-1" > kernel.perf_event_paranoid`. 

​			This configuration allows non-root users to monitor system events and parameters.

​		3,  The default time zone in the pod is `utc0`. Do not change this.



##### Execution advice:

​		1, The default container start time is 2mins after src/start-perf starts. So if the image is too slow to download, it is recommended to download the image beforehand. Or build it in the image folder. 

​			`docker build -t kubeovn/perf:v0.1 . `	

​			We also encourage users to create test commands as they wish and build them into images. Simply save the results to the `/results` folder. K8s-autoperf will automatically retrieve the results.

​		2, Default test time 60s. 

​		3, Delete or migrate the results when you are done testing, otherwise you will rebuild the `svg` file several times (which will take more time but not change the results).

​		For other configurations see --help

```shell
❯ python3 ./src/start-perf.py --help
usage: start-perf.py [-h] [--output OUTPUT] [--duration DURATION]
                     [--msglen MSGLEN] [--intervals INTERVALS] [--port PORT]
                     [--protocol PROTOCOL] [--clienthost CLIENTHOST]
                     [--serverhost SERVERHOST] [--svcmode SVCMODE]
                     [--epnumber EPNUMBER] [--svcport SVCPORT]

auto Perf for kubernetes

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT       output folder
  --duration DURATION   test duration, integer
  --msglen MSGLEN       sockperf message length, integer
  --intervals INTERVALS
                        intervals between sampling, integer
  --port PORT           port for test, between 1024 and 65535
  --protocol PROTOCOL   protocol to test, "tcp" or "udp"
  --clienthost CLIENTHOST
                        true if client in host mode, default false
  --serverhost SERVERHOST
                        true if server in host mode, default false
  --svcmode SVCMODE     true if perf for service ip, default false
  --epnumber EPNUMBER   numbers of endpoints in svc mode, integer, default 1
  --svcport SVCPORT     svc port, between 1024 and 65535, integer, default
                        11111
```

