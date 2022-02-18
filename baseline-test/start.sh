#!/bin/bash

SERVERIP="11.11.11.12"
CPULIM=$(($(cat /proc/cpuinfo  | grep "processor"  | wc -l)/2))
CPUREQ=$(($CPULIM-1))

showHelp(){
  echo "Available Subcommands:"
  echo "  all    invoke all tests, including node2node, pod2pod"
  echo "  pod   invoke pod2pod test"
}

runnode(){
   sed -e "s/CPULIM/${CPULIM}/g" -e "s/CPUREQ/${CPUREQ}/g" -e "s/IFHOST/true/g"  ./Server.yaml > /tmp/Server-hostnet.yaml
   kubectl apply -f /tmp/Server-hostnet.yaml
   kubectl rollout status deploy qperf-server
   sed -e "s/CPULIM/${CPULIM}/g" -e "s/CPUREQ/${CPUREQ}/g" -e "s/SERVERIP/${SERVERIP}/g" -e "s/IFHOST/true/g" ./Client.yaml > /tmp/Client-hostnet.yaml
   kubectl apply -f /tmp/Client-hostnet.yaml
   while [[ $(kubectl get jobs qperf-client -o=jsonpath='{.status.conditions[0].type}') != "Complete" ]];
   do
     sleep 1;
   done
	 delAll
}

runpod(){
   sed -e "s/CPULIM/${CPULIM}/g" -e "s/CPUREQ/${CPUREQ}/g" -e "s/IFHOST/false/g"  ./Server.yaml > /tmp/Server-podnet.yaml
   kubectl apply -f /tmp/Server-podnet.yaml
   kubectl rollout status deploy qperf-server
   PODSERVERIP=$(kubectl get pods -l app=qperf-server -o=jsonpath='{.items[0].status.podIPs[0].ip}')
   sed -e "s/CPULIM/${CPULIM}/g" -e "s/CPUREQ/${CPUREQ}/g" -e "s/SERVERIP/${PODSERVERIP}/g" -e "s/IFHOST/false/g" ./Client.yaml > /tmp/Client-podnet.yaml
   kubectl apply -f /tmp/Client-podnet.yaml
   while [[ $(kubectl get jobs qperf-client -o=jsonpath='{.status.conditions[0].type}') != "Complete" ]];
   do
     sleep 1;
   done
	 delAll
}

runsvc(){
  sed -e "s/CPULIM/${CPULIM}/g" -e "s/CPUREQ/${CPUREQ}/g" -e "s/IFHOST/false/g"  ./Server.yaml > /tmp/Server-podnet.yaml
  kubectl apply -f /tmp/Server-podnet.yaml
  kubectl rollout status deploy qperf-server
  SERVERIP=$(kubectl get svc qperf-server -o=jsonpath='{.spec.clusterIPs[0]}')
  sed -e "s/CPULIM/${CPULIM}/g" -e "s/CPUREQ/${CPUREQ}/g" -e "s/SERVERIP/${SERVERIP}/g" -e "s/IFHOST/false/g" ./Client.yaml > /tmp/Client-podnet.yaml
  kubectl apply -f /tmp/Client-podnet.yaml
  while [[ $(kubectl get jobs qperf-client -o=jsonpath='{.status.conditions[0].type}') != "Complete" ]];
  do
    sleep 1;
  done
  delAll
}

function delAll {
  kubectl delete deployment qperf-server
  kubectl delete jobs qperf-client
  kubectl delete cm qperf-client
  kubectl delete svc qperf-server
}

function quit {
	delAll
	exit 0
}
trap quit INT TERM

if [ $# -lt 1 ]; then
  showHelp
  exit 0
else
  subcommand="$1"; shift
fi

case $subcommand in
  all)
    runnode
    runpod
    ;;
  pod)
    runpod
    ;;
  svc)
    runsvc "$@"
    ;;
  *)
    showHelp
    ;;
esac