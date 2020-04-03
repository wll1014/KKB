#!/bin/bash
. /opt/data/luban/shells/kdfunctions
ip_info=$1
upucore_ips=($(grep upucore $ip_info | cut -d"=" -f 2))
# echo ${upucore_ips[@]}
upucore_ha_port=2105
upucore_port=2205
path=$3

check_link_status()
{
    ip=$1
    echo | telnet $ip $upucore_ha_port  2>/dev/null| grep -q "Connected"
    link_status=$?
    link_err_info="connet 2105 failed"
    link_check_method="telnet $ip $upucore_ha_port"
}


check_cluster_status()
{
    ip=$1
    upucore_moid=$(echo "/opt/midware/zookeeper/bin/zkCli.sh get /monitor_lock/domain/mooooooo-oooo-oooo-oooo-topplatfoorm/upucore" |ssh -o StrictHostKeyChecking=no -p 33332 root@$ip  2>/dev/null | grep server_moid | awk -F"\"" '{print $4}')
    if [ ! -z $upucore_moid ];then
        moid_num=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$ip cat /opt/data/config/luban_config/deploy.json | grep $upucore_moid | wc -l)
        proc_num=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$ip ps aux | grep -w "/opt/mcu/upucore" | grep -v grep | wc -l)
        if [ $moid_num -eq 1 -a $proc_num -eq 2 ];then
            flag=0
        elif [ $moid_num -eq 0 -a $proc_num -eq 0 ];then
            flag=0
        else
            flag=1
        fi
        upucore_err_info="upucore is not need start"
        upucore_check_method="/opt/midware/zookeeper/bin/zkCli.sh get /monitor_lock/domain/mooooooo-oooo-oooo-oooo-topplatfoorm/upucore"
    else
        flag=1
        upucore_err_info="upucore is not create monitor_lock"
        upucore_check_method="/opt/midware/zookeeper/bin/zkCli.sh get /monitor_lock/domain/mooooooo-oooo-oooo-oooo-topplatfoorm/upucore"
    fi
}

for upucore_ip in ${upucore_ips[@]};do
    echo "[upucore_$upucore_ip]" >>$path
    check_link_status $upucore_ip
    check_cluster_status $upucore_ip
    if [ $link_status -eq 0 -a $flag -eq 0 ];then
        echo "status = 0" >>$path
        echo "ip = $upucore_ip" >>$path
    elif [ $link_status -eq 0 -a $flag -eq 1 ];then
        echo "status = 1" >>$path 
        echo "ip = $upucore_ip" >>$path
        echo "err_info_1 = $upucore_err_info" >>$path
        echo "check_method_1 = $upucore_check_method" >>$path
    else
        echo "status = 1" >>$path
        echo "ip = $upucore_ip" >>$path
        echo "err_info_1 = $link_err_info" >>$path
        echo "check_method_1 = $link_check_method" >>$path
    fi
done
 