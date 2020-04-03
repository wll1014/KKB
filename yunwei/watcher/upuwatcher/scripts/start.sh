#!/usr/bin/env bash

path=$(cd $(dirname ${0});pwd)

if [ $# -ne 2 ];then
    echo "args error"
    exit 1
fi

#parm1 mq地址，多个以英文逗号','隔开
#parm2 平台域moid
#desc 启动mqwatcher
function start_wathcer() {
    upu_addr=${1}
    platfrom_moid=${2}
    export LD_LIBRARY_PATH=/opt/mcu/sodir64:$LD_LIBRARY_PATH
    PYTHONPATH=${path}/../lib/python3.5/site-packages/ /opt/midware/python3/bin/python3 ${path}/../upu_watcher.py --upu-addr=${upu_addr} --platform-moid=${platfrom_moid} 1>/dev/null 2>&1 &
}

start_wathcer ${1} ${2}
