#!/usr/bin/env bash
#执行脚本

exec_script=$1
shift

pids=$(ps -ef | grep "${exec_script}" | grep "elasticdump" | grep -v "grep" | awk '{print $2}')
if [ -z "${pids}" ]; then
    /bin/bash "${exec_script}" "$@" "elasticdump" &>/dev/null &
    dump_pid=$!
    echo "dump_pid:${dump_pid}"
    exit 0
else
    echo "有正在执行的elasticdump，请等待..."
    exit 2
fi
