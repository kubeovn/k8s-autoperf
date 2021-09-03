## k8s-autoperf

##### 这是什么:

​		k8s-autoperf 是一套用于在 Kubernetes 集群内完成自动化网络性能测试的小工具. 它能够完成自动化的性能测试 server/client pod 部署, 自动化的网络性能测试, 以及在测试期间的主机状态, 性能监控. 

​		最终, 以上测试与监控的结果都将会以文件与火焰图的形式输出到本地的`./result/`文件夹下. 每次测试的结果都会以测试时间为文件名进行区分.



##### 如何使用:

​		安装依赖(以 centos 为例):

```shell
yum install python3 python3-pip3 perf -y
pip3 install pyyaml
```

​		为测试 client 的所在节点打标, 该步骤确定 perf-client 的所在节点, `CLIENT-NODE` 是该节点名:

```shell
kubectl label nodes CLIENT-NODE perf-role=client
```

​		为测试 server 的所在节点打标, 该步骤确定 perf-server 的所在节点, `SERVER-NODE` 是该节点名:

```shell
kubectl label nodes SERVER-NODE perf-role=server
```

​		为需要做监控的节点打标. 可以为多个节点打标, 例如为 client 和 server 所在的节点都打标. 在测试时会监控主机的cpu/火焰图/内存等资源(监控内容可增加).

```shell
kubectl label nodes SERVER-NODE perf-monitor=yes
kubectl label nodes CLIENT-NODE perf-monitor=yes
```

​		进入 `src` 目录并启动测试, 等待测试完成后, 在 `./result` 目录下可找到测试结果

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

​		时延测试结果由 `Delay` 结尾的文件保存, 带宽测试结果由 `PT` (Passthought)结尾的文件保存, 带宽测试期间的测试节点火焰图数据由 `perf.data` 保存.  生成的火焰图是同名的`svg` 文件.  `cpu` 使用情况由 `perf-NODE-TIMEcpu` 的文件保存. 系统使用情况由 `perf-NODE-TIMEtop` 的文件保存.



##### 使用样例:

1, 测试pod之间直连的网络性能

```shell
python3 ./start-perf.py
```

2, 测试一个 pod 以 service ip 为目的 ip 访问集群内另一个服务时的网络性能. 可以指定 endpoint 的数量.

```shell
python3 ./start-perf.py --svcport true  --epnumber 2
```

3, 测试一个 pod 访问另外一个以 hostnet 模式部署的 pod 时的性能(或反过来).

```shell
python3 ./start-perf.py --serverhost true
```



##### 执行流程:

​		src/start-pef 设定参数和启动时间, 基于模板配置临时yaml文件(可在 /tmp/ 目录下找到并检查验证). 

​		临时yaml文件会被下发到k8s. client pod 在启动时间启动测试, monitor pod监控并存储结果至文件.

​		等待一定时间后, start-perf 回收数据, 删除测试资源. 



##### 执行要求:

​		1, 必须要有一个 node 的 label 中存在 perf-role=server, 该 node 为测试中的服务端所在 node. 必须有另一个不同的node被标记为perf-role=client, 该 node 作为测试中的客户端所在node. 该要求会在执行测试前检查.

​		2, 目前 monitor 端是作为 root 执行. 若认为存在安全隐患, 也可以在需要部署 monitor 的 node上, 提前执行命令 

​			`echo "-1" > kernel.perf_event_paranoid`. 该配置可以让非 root 用户也能够监控系统事件和参数.

​		3, pod 内时间默认以 `utc0` 为准. 不要修改.



##### 执行建议:

​		1, 默认的容器内程序启动时间为 src/start-perf 启动后的 2mins. 所以如果镜像下载过慢, 建议预先下载好镜像. 或是通过 image 文件夹下进行打包. `docker build -t kubeovn/perf:v0.1 .`	

​		2, 默认测试时间60s. 

​		3, 测试完毕后及时删除或迁移结果, 否则会多次重建`svg`文件(会多耗时间但是不会改变结果).

​		其他配置见 --help

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

