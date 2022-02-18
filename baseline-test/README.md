#### 使用测试工具:

##### 使用条件:

		1. default ns 下不要有名为 qperf-server 的 deployment, 名为 qperf-client 的 jobs 和 configmap
		1. 如果没有网络的话需要预先下载好镜像
		1. 测试机的CPU数量大于等于4



##### 使用过程:

预先给用于部署测试 server pod 和测试 client pod 的 node 打标, 支持用户自选 server pod 和 client pod 所在 node. 用户只需要为对应 node 打标即可:

```bash
# 让 server pod 和 client pod 处于不同的 node 进行测试
$ kubectl label nodes ty-c2-medium-x86-02 perfServer=true
$ kubectl label nodes ty-c2-medium-x86-01 perfClient=true

# 让 server pod 和 client pod 在同一个 node 上测试
$ kubectl label nodes ty-c2-medium-x86-02 perfServer=true
$ kubectl label nodes ty-c2-medium-x86-02 perfClient=true
```

可以进行完全模式测试, 该模式下会先测试 node 间的网络情况. 再测试 pod 间的网络情况.

```bash
$ bash ./start all
```

也可以只进行 pod2pod 的网络情况测试:

```bash
$ bash ./start pod
```

结果会存储在当前文件夹下的 `result` 子文件夹中.