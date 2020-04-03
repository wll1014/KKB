#!/bin/bash
. /opt/data/luban/shells/kdfunctions
ip_info=$1
upu_ips=($(grep -w upu $ip_info | cut -d"=" -f 2))
# echo ${upu_ips[@]}
upu_ha_port=2100
upu_port=2200
path=$3

check_link_status()
{
    ip=$1
    echo | telnet $ip $upu_ha_port  2>/dev/null| grep -q "Connected"
    link_status=$?
    link_err_info="connet 2100 failed"
    link_check_method="telnet $ip $upu_ha_port"
}


check_cluster_status()
{
    ip=$1
    upu_num=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$ip /opt/mcu/upu/bin/upu cluster_nodes | grep -w upu|wc -l)
    cfg_node_num=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$ip cat /opt/data/upu/cluster_info.ini | grep nodes |cut -d '=' -f2|awk -F ',' '{print NF}')
    upu_err_info="running nodes is not 2"
    upu_check_method="/opt/mcu/upu/bin/upu cluster_nodes"
}

upu_ip_num=${#upu_ips[@]}
if [ $upu_ip_num -eq 2 ];then
    for upu_ip in ${upu_ips[@]};do
        echo "[upu_$upu_ip]" >>$path 
        check_link_status $upu_ip
        check_cluster_status $upu_ip
        if [ $link_status -eq 0 -a $upu_num -eq $cfg_node_num ];then
            echo "status = 0" >>$path
            echo "ip = $upu_ip" >>$path
        elif [ $link_status -eq 0 -a $upu_num -ne $cfg_node_num ];then
            echo "status = 1" >>$path
            echo "ip = $upu_ip" >>$path 
            echo "err_info_1 = $upu_err_info"  >>$path
            echo "check_method_1 = $upu_check_method" >> $path
        else
            echo "status = 1" >>$path
            echo "ip = $upu_ip" >>$path
            echo "err_info_1 = $link_err_info"  >>$path
            echo "check_method_1 = $link_check_method" >> $path
        fi
    done
elif [ $upu_ip_num -ne 0 ];then
    echo "[upu_$upu_ips]" >>$path
    check_link_status $upu_ips
    if [ $link_status -eq 0 ];then
        echo "status = 0" >>$path
        echo "ip = $upu_ips" >>$path
    else
        echo "status = 1" >>$path
        echo "ip = $upu_ips" >>$path
        echo "err_info_1 = $link_err_info"  >>$path
        echo "check_method_1 = $link_check_method" >> $path
    fi
fi
