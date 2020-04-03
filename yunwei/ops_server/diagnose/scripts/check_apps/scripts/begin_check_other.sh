#!/usr/bin/env bash


cur_dir=$(cd $(dirname ${0});pwd)

check_apps_path=/opt/data/ops/media/check_apps
ip_info=${check_apps_path}/conf/ip_info.ini
ips=($(grep -w machine $ip_info | cut -d"=" -f 2))
result=${check_apps_path}/other.ini
deploy_ini=/opt/data/config/luban_config/deploy.ini

echo > ${result}

# 其他脚本已经检测过的app数组
check_done_apps=(aps cmdataproxy cmu css pas rms upucore upu dss-master media-master modbcore modb \
    mysql ejabberd glusterfs glusterfsd rabbitmq redis zookeeper nms_starter nms_webserver susmgr 8000aagent)
for ip in ${ips[@]}; do
    {
    apps=()
    badapp=()
    goodappnum=0
    badappnum=0
    now_server_list=$(ssh -o StrictHostKeyChecking=no -p 33332 root@${ip} "egrep ^server_list ${deploy_ini}" 2>/dev/null)
    now_app_list=$(ssh -o StrictHostKeyChecking=no -p 33332 root@${ip} "egrep ^app_list ${deploy_ini}" 2>/dev/null)
    if [ -z "${now_server_list}" ];then
        err_info="${ip} ssh cannot connected,no deploy.ini to read."
        check_method="ssh -p 33332 root@${ip}"
        echo "[machine_$ip]" >>$result
        echo "status = 1" >>$result
        echo "ip = $ip" >>$result
        echo "err_info_1 = $err_info" >>$result
        echo "check_method_1 = $check_method" >>$result
        continue
    fi
    now_server_list=(${now_server_list//server_list/ })
    now_server_list=(${now_server_list[@]//=/ })
    now_server_list=(${now_server_list[@]//,/ })
    now_app_list=(${now_app_list//app_list/ })
    now_app_list=(${now_app_list[@]//=/ })
    now_app_list=(${now_app_list[@]//,/ })

    echo "[machine_$ip]" >>$result

    for app in ${now_server_list[@]}; do
        if [[ "${check_done_apps[@]}" =~ "${app}" ]] || [ "$app" == "java" ];then
            :
        else
            if [[ "${now_app_list[@]}" =~ "${app}" ]];then
                apps=(${apps[@]} ${app})
                ssh -o StrictHostKeyChecking=no -p 33332 root@${ip} "/opt/mcu/${app}/shells/status.sh &>/dev/null"
                if [ $? -eq 0 ];then
                    let "goodappnum+=1"
                else
                    let "badappnum+=1"
                    badapp=(${badapp[@]} ${app})
                fi
            fi
        fi
    done
    if [ ${badappnum} -eq 0 ];then
        echo "status = 0" >>$result
    else
        echo "status = 1" >>$result
        echo "err_info_1 = [${badapp[@]}] is not normally" >>$result
        echo "check_method_1 = /opt/mcu/{${badapp[@]}}/shells/status.sh" >>$result
    fi
    echo "ip = $ip" >>$result
    echo "check_apps = ${apps[@]}" >>$result
    }
done

