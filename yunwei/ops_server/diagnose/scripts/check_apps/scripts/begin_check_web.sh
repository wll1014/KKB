#!/bin/bash
# web应用状态检测


cur_dir=$(cd $(dirname ${0});pwd)

check_apps_path=/opt/data/ops/media/check_apps
ip_info=${check_apps_path}/conf/ip_info.ini
web_ips=($(grep -w web $ip_info | cut -d"=" -f 2))
result=${check_apps_path}/web.ini
deploy_ini=/opt/data/config/luban_config/deploy.ini
curl_cmd="curl --connect-timeout 1 --max-time 3 -o /dev/null -s -w %{http_code} "

echo > ${result}

webcheckall=("amc" "amcapi" "apicomet" "bmc" "serviceCore" "ssoCore" "apiCore" \
    "cmc" "service" "sso" "api" "api5" "ssuweb" "jms")

for web_ip in ${web_ips[@]};do
    apps=()
    badapps=()
	goodappnum=0
    badappnum=0
	now_server_list=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$web_ip "egrep ^server_list ${deploy_ini}" 2>/dev/null)
	if [ -z "${now_server_list}" ];then
	    web_err_info="${web_ip} ssh cannot connected,no deploy.ini to read."
	    web_check_method="ssh -p 33332 root@${web_ip}"
        echo "[web_$web_ip]" >>$result
	    echo "status = 1" >>$result
    	echo "ip = $web_ip" >>$result
    	echo "err_info_1 = $web_err_info" >>$result
    	echo "check_method_1 = $web_check_method" >>$result
	    continue
	fi
    now_server_list=(${now_server_list//server_list/ })
    now_server_list=(${now_server_list[@]//=/ })
    now_server_list=(${now_server_list[@]//,/ })

	echo "[web_$web_ip]" >>$result
	for app in ${webcheckall[@]};do
	    if [[ "${now_server_list[@]}" =~ "${app}" ]];then
            for now_server in ${now_server_list[@]}; do
                if [ "x${now_server}" = "x${app}" ];then
                    apps=(${apps[@]} ${app})
                    if [ x"${app}" = x"apicomet" ];then
                        app_status=$(${curl_cmd} http://${web_ip}:8080/${app}/state.html 2>&1)
                    elif [ x"${app}" = x"cmc" ];then
                        meeting_status=$(${curl_cmd} http://${web_ip}:8080/meeting/check 2>&1)
                        meetingapi_status=$(${curl_cmd} http://${web_ip}:8080/meetingapi/check 2>&1)
                        app_status=$[ (${meeting_status} + ${meetingapi_status}) / 2 ]
                    elif [ x"${app}" = x"api" ];then
                        api_status=$(${curl_cmd} http://${web_ip}:8080/${app}/check 2>&1)
                        api5_status=$(${curl_cmd} http://${web_ip}:8080/${app}5/check 2>&1)
                        app_status=$[ (${api_status} + ${api5_status}) / 2 ]
                    else
                        app_status=$(${curl_cmd} http://${web_ip}:8080/${app}/check 2>&1)
                    fi
                    if [[ $app_status -ne 200 ]];then
                        echo $app_status
                        echo $app
                        badapps=(${badapps[@]} ${app})
                        flag=1
                        let "badappnum+=1"
                    elif [[ $app_status -eq 200 ]];then
                        goodappnum=$(expr $goodappnum + 1)
                    fi
                fi
            done
	    fi
    done
    if [ ${badappnum} -eq 0 ];then
    	echo "status = 0" >>$result
    	echo "ip = $web_ip" >>$result
    else
        web_err_info="check status is not 200"
        web_check_method="curl http://${web_ip}:8080/[${badapps[@]}]/check"
    	echo "status = 1" >>$result
    	echo "ip = $web_ip" >>$result
    	echo "err_info_1 = $web_err_info" >>$result
    	echo "check_method_1 = $web_check_method" >>$result
    fi
    echo "check_apps = ${apps[@]}" >>$result
done

