#!/usr/bin/env bash

path=$(cd $(dirname ${0});pwd)

if [[ $# -lt 2 ]];then
    echo "args error"
    exit 1
fi

#parm1 mq地址，多个以英文逗号','隔开
#parm2 平台域moid
#desc 启动mqwatcher
function start_wathcer() {
    mq_addr=${1}
    platform_moid=${2}
    kafka_addr=${3:-127.0.0.1}
    kafka_port=${4:-9092}

    # 环境变量同时加载自己的库和公共库
    PYTHONPATH=${path}/../lib/python3.5/site-packages/:${path}/../common_lib/python3.5/site-packages/ \
    /opt/midware/python3/bin/python3 ${path}/../mqwatcher.py \
    --mq-addr=${mq_addr} \
    --platform-moid=${platform_moid} \
    --kafka-addr=${kafka_addr} \
    --kafka-port=${kafka_port} &
}

start_wathcer ${1} ${2} ${3} ${4}
