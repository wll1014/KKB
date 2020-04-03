#!/bin/bash
. /opt/data/luban/shells/kdfunctions
ip_info=$1
redis_ips=($(grep redis $ip_info | cut -d"=" -f 2))
# echo ${redis_ips[@]}
redis_ha_port=6379
redis_port=7379
path=$3

check_link_status()
{
    ip=$1
    /opt/midware/redis/bin/redis-cli -a KedaRedis16 -h $ip ping >/dev/null
    link_status=$?
    link_err_info="connet 6379 failed"
    link_check_method="/opt/midware/redis/bin/redis-cli -a KedaRedis16 -h $ip ping"
}

check_role()
{
    ip=$1
    dms_status=$(curl --connect-timeout 1 --max-time 3 -s -I http://${ip}:9203 | grep HTTP/1.0 | cut -d" " -f 2)
    role_status=$(/opt/midware/redis/bin/redis-cli -a KedaRedis16 -h $ip -p 7379 info Replication | grep role | cut -d":" -f 2)
    role_err_info="redis role don't match"
    role_check_method="/opt/midware/redis/bin/redis-cli -a KedaRedis16 -h $ip -p 7379 info Replication"
}

for redis_ip in ${redis_ips[@]};do
    echo "[redis_${redis_ip}]" >>$path
    check_link_status $redis_ip
    check_role $redis_ip
    if [ $link_status -eq 0 ];then
        if [[ $dms_status -eq 200 && x"$role_status" =~ x"master" ]];then
            echo "status = 0" >>$path
            echo "ip = $redis_ip" >>$path
        elif [[ $dms_status -eq 503 && x"$role_status" =~ x"slave" ]];then
            echo "status = 0" >>$path
            echo "ip = $redis_ip" >>$path
        else
            echo "status = 1" >>$path
            echo "ip = $redis_ip" >>$path
            echo "err_info_1 = $role_err_info" >>$path
            echo "check_method_1 = $role_check_method" >>$path
        fi
    else
        echo "status = 1" >>$path
        echo "ip = $redis_ip" >>$path
        echo "err_info_1 = $link_err_info" >>$path
        echo "check_method_1 = $link_check_method" >>$path
    fi
done
