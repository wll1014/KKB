#!/bin/bash
. /opt/data/luban/shells/kdfunctions
ip_info=$1
ejabberd_ips=($(grep ejabberd $ip_info | cut -d"=" -f 2))
# echo ${ejabberd_ips[@]}
ejabberd_ha_port=5222
ejabberd_port=6222
path=$3

check_link_status()
{
    ip=$1
    echo | telnet $ip $ejabberd_ha_port  2>/dev/null| grep -q "Connected"
    link_status=$?
    link_err_info="connet 5222 failed"
    link_check_method="telnet $ip $ejabberd_ha_port"
}

check_cluster()
{
    ip=$1
    ejabberd_num=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$ip /opt/midware/mo_ejabberd/bin/ejabberdctl mnesia info | grep "running db nodes" | grep -o "@" | wc -l)
    cfg_ejabberd_num=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$ip cat /opt/data/ejabberd/cluster_info.ini | grep nodes |cut -d '=' -f2|awk -F ',' '{print NF}')
    cluster_err_info="running db nodes is not 2"
    cluser_check_method="/opt/midware/mo_ejabberd/bin/ejabberdctl mnesia info | grep 'running db nodes'"
}

ejabberd_ip_num=${#ejabberd_ips[@]}
if [ $ejabberd_ip_num -eq 2 ];then
    for ejabberd_ip in ${ejabberd_ips[@]};do
        echo "[ejabberd_$ejabberd_ip]" >>$path 
        check_link_status $ejabberd_ip
        check_cluster $ejabberd_ip
        if [ $link_status -eq 0 -a $ejabberd_num -eq $cfg_ejabberd_num ];then
            echo "status = 0" >>$path
            echo "ip = $ejabberd_ip" >>$path
        elif [ $link_status -eq 0 -a $ejabberd_num -ne $cfg_ejabberd_num ];then
            echo "status = 1" >>$path
            echo "ip = $ejabberd_ip" >>$path 
            echo "err_info_1 = $cluster_err_info"  >>$path
            echo "check_method_1 = $cluser_check_method" >> $path
        else
            echo "status = 1" >>$path
            echo "ip = $ejabberd_ip" >>$path
            echo "err_info_1 = $link_err_info"  >>$path
            echo "check_method_1 = $link_check_method" >> $path
        fi
    done
elif [ $ejabberd_ip_num -ne 0 ];then
    echo "[ejabberd_$ejabberd_ips]" >>$path
    check_link_status $ejabberd_ips
    if [ $link_status -eq 0 ];then
        echo "status = 0" >>$path
        echo "ip = $ejabberd_ips" >>$path
    else
        echo "status = 1" >>$path
        echo "ip = $ejabberd_ips" >>$path
        echo "err_info_1 = $link_err_info"  >>$path
        echo "check_method_1 = $link_check_method" >> $path
    fi
fi


