#!/usr/bin/env bash
# 平台业务状态检测

cur_dir=$(cd $(dirname ${0});pwd)
cd ${cur_dir}
check_apps=(aps cmdataproxy cmu css pas rms upu dss-master media-master modb)

check_apps_path=/opt/data/ops/media/check_apps
ip_info=${check_apps_path}/conf/ip_info.ini
log_path=${check_apps_path}/log/platform/
result=${check_apps_path}/platform.ini
mkdir -p ${log_path} $(dirname ${result})

echo > ${result}
rm -f ${log_path}/*

for app in ${check_apps[@]}; do
    scripts=($(ls ./check_${app}*.sh))
    for script in ${scripts[@]}; do
        ${script} ${ip_info} ${log_path} ${result}
    done
done

