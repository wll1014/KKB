#!/usr/bin/env bash

params_1=${1}
params_2=${2}

# 将第一个参数输出至标准输出
echo ${params_1:-'params_1 is null'}

# 存在第二个参数，将第二个参数重定向输出到错误输出
# 不存在则将执行时间重定向输出到错误输出
if [[ -z ${params_2} ]];then
    echo $(date) 1>&2
    ret=1
else
    echo ${params_2} 1>&2
    ret=0
fi

exit ${ret}
