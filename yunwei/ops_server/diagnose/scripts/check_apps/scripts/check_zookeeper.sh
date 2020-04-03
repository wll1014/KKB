#!/bin/bash
. /opt/data/luban/shells/kdfunctions
ip_info=$1
zk_ips=($(grep -w "zookeeper" $ip_info | cut -d"=" -f 2))
# echo ${zk_ips[@]}
path=$3

check_status()
{
    ip=$1
    dms_status=$(curl -s -I http://${ip}:9202 | grep HTTP/1.0 | cut -d" " -f 2)
    role_status=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$ip python3 /opt/midware/dms/apps/elector/elector_cli.py ${ip}:8355 role | awk '{print $2}')
    zk_err_info="zk role is not match"
    zk_check_method="curl -s -I http://${ip}:9202"
}

for zk_ip in ${zk_ips[@]};do
    echo "[zk_$zk_ip]" >>$path
    check_status $zk_ip
    if [ $dms_status -eq 200 -a x"$role_status" == x"leader" ];then
        echo "status = 0" >>$path
        echo "ip = $zk_ip" >>$path
    elif [ $dms_status -eq 503 -a x"$role_status" == x"follower" ];then
        echo "status = 0" >>$path
        echo "ip = $zk_ip" >>$path
    else
        echo "status = 1" >>$path
        echo "ip = $zk_ip" >>$path
        echo "err_info_1 = $zk_err_info" >>$path
        echo "check_method_1 = $zk_check_method" >>$path
    fi
done
