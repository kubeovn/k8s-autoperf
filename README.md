## k8s-autoperf

##### 如何使用:

​		安装依赖(以 centos 为例):

```shell
yum install python3 pip3
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

​		进入 `src` 目录并启动测试, 等待测试完成后, 在 `./result` 目录下可找到测试结果

```shell
[root@perf-c3-small-x86-01 src]# python3 ./start-perf.py
deployment.apps/kubeovn-perfserver created

server is ready
deployment.apps/kubeovn-perfclient created

deployment.apps/kubeovn-perfmonitor created

retrieve finished
retrieve finished
deployment.apps "kubeovn-perfclient" deleted
deployment.apps "kubeovn-perfserver" deleted
deployment.apps "kubeovn-perfmonitor" deleted

[root@perf-c3-small-x86-01 src]# ls ./result/
kubeovn-perfclient-6d54b656c4-sgwrh-10.16.0.13-sockperfDelay      kubeovn-perfclient-6d54b656c4-sgwrh-10.16.0.13-sockperfPT      perf-c3-small-x86-02-perf-07:45:46top  perf-c3-small-x86-02-perf-07:45:46cpu
kubeovn-perfclient-6d54b656c4-sgwrh-10.16.0.13-sockperfDelay.err  kubeovn-perfclient-6d54b656c4-sgwrh-10.16.0.13-sockperfPT.err  perf.data
```

​		时延测试结果由 `Delay` 结尾的文件保存, 带宽测试结果由 `PT` (Passthought)结尾的文件保存, 带宽测试期间的测试节点火焰图由 `perf.data` 保存. `cpu` 使用情况由 `perf-NODE-TIMEcpu` 的文件保存. 其他使用情况由 `perf-NODE-TIMEcop` 的文件保存.



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

​		其他配置见 --help

```shell
❯ python3 ./src/start-perf.py --help
usage: start-perf.py [-h] [--output OUTPUT] [--duration DURATION] [--msglen MSGLEN] [--intervals INTERVALS] [--port PORT] [--protocol PROTOCOL]

auto Perf for kubernetes

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT       output folder
  --duration DURATION   test duration
  --msglen MSGLEN       sockperf message length
  --intervals INTERVALS
                        intervals between sampling
  --port PORT           port for test
  --protocol PROTOCOL   protocol for test
```

