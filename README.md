## k8s-autoperf

##### 执行流程:

​		src/start-pef 设定参数和启动时间, 基于模板配置临时yaml文件(可在 /tmp/ 目录下找到并检查验证). 

​		临时yaml文件会被下发到k8s. client pod 在启动时间启动测试, monitor pod监控并存储结果至文件.

​		等待一定时间后, start-perf 回收数据, 删除测试资源. 



##### 执行要求:

​		1, 必须要有一个 node 的 label 中存在 perf-role=server, 该 node 为测试中的服务端所在 node. 必须有另一个不同的node被标记为perf-role=client, 该 node 作为测试中的客户端所在node. 该要求会在执行测试前检查.

​		2, 目前 monitor 端是作为 root 执行. 若认为存在安全隐患, 也可以在需要部署 monitor 的 node上, 提前执行命令 

​			`echo "-1" > kernel.perf_event_paranoid`. 该配置可以让非 root 用户也能够监控系统事件和参数.

​		3, 所有 node 和 pod 的时间应该完成同步. 该要求暂无检查.



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

