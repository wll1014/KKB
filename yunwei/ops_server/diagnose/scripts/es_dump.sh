#!/usr/bin/env bash
#使用elasticdump导出es数据到文件

if [ $# -ne 5 ]; then
    echo "参数错误，dump_input:$1  dump_output:$2  dump_type:$3  dump_search_body:$4  dump_file_name:$5"
    exit 1
fi

dump_input=$1
dump_output=$2
dump_type=$3
dump_search_body=$4
dump_file_name=$5

elasticdump_cmd="elasticdump"
pids=$(ps -ef | grep "node" | grep "elasticdump" | grep "${dump_file_name}.json" | grep -v "grep" | awk '{print $2}')
if [ -z "${pids}" ]; then
    ${elasticdump_cmd} --input=${dump_input} \
    --output=${dump_output} \
    --type=${dump_type} \
    --overwrite=true \
    --searchBody=${dump_search_body} &>/dev/null &
    dump_pid=$!
    echo "dump_pid:${dump_pid}"
    exit 0
else
    echo "有正在执行的elasticdump，请等待..."
    exit 2
fi
