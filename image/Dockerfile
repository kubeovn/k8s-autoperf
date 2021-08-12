FROM centos:7 as builder
RUN yum install git wget gcc autoconf libtool gcc-c++ make -y  && \
    wget https://github.com/HewlettPackard/netperf/archive/refs/tags/netperf-2.7.0.tar.gz && \
    tar -zxvf ./netperf-2.7.0.tar.gz  && \
    cd ./netperf-netperf-2.7.0/  && \
    ./configure  && \
    make && make install  && \
    cd ..  && \
    git clone https://github.com/Mellanox/sockperf.git && \
    cd ./sockperf  && \
    ./autogen.sh  && \
    ./configure  && \
    make && make install
FROM centos:7
WORKDIR /
COPY --from=builder /usr/local/bin/netperf    /usr/local/bin/netperf
COPY --from=builder /usr/local/bin/sockperf   /usr/local/bin/sockperf
COPY --from=builder /usr/local/bin/netserver  /usr/local/bin/netserver
RUN yum install iperf3 qperf perf python3 sysstat -y && \
    mkdir /result
COPY startSr.sh /startSr.sh
COPY startTest.py  /startTest.py
COPY startMonit.py /startMonit.py
