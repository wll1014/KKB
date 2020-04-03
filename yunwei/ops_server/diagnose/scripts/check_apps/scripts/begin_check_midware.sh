#!/usr/bin/env bash
# 组件状态检测

cur_dir=$(cd $(dirname ${0});pwd)
cd ${cur_dir}
check_apps=(mysql ejabberd glusterfs rabbitmq redis zookeeper)

check_apps_path=/opt/data/ops/media/check_apps
ip_info=${check_apps_path}/conf/ip_info.ini
log_path=${check_apps_path}/log/midware/
result=${check_apps_path}/midware.ini
mkdir -p ${log_path} $(dirname ${result})

echo > ${result}
rm -f ${log_path}/*

for app in ${check_apps[@]}; do
    scripts=($(ls ./check_${app}*.sh 2>/dev/null))
    for script in ${scripts[@]}; do
        ${script} ${ip_info} ${log_path} ${result}
    done
done

