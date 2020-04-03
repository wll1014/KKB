#!/bin/bash
. /opt/data/luban/shells/kdfunctions
ip_info=$1
gfs_ips=($(grep -w "glusterfs" $ip_info | cut -d"=" -f 2))
path=$3

check_volume_status()
{
    ip=$1
    ssh -o StrictHostKeyChecking=no -p 33332 root@$ip gluster volume info | grep -q common_app
    volume_status=$?
    volume_err_info="no volume,please create"
    volume_check_method="gluser volume info"
}


check_cluster()
{
    ip=$1
    brick_num=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$ip gluster volume info |egrep -o -i  'Brick[1-9]+'|sort|uniq|wc -l)
    node_num=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$ip cat /opt/mcu/glusterfsd/shells/cluster_info.ini 2>>/dev/null|grep -i "nodes"|cut -d '=' -f2|awk -F ',' '{print NF}')
    cluster_err_info="brick number or nodes number is not 2"
    cluster_check_method="'gluster volume info' check brick info"
}


gfs_num=${#gfs_ips[@]}
if [ $gfs_num -eq 2 ];then
    for gfs_ip in ${gfs_ips[@]};do
        echo "[gfs_$gfs_ip]" >>$path
        check_cluster $gfs_ip
        if [[ $volume_status -eq 0 && $brick_num -eq $node_num ]];then
            echo "status = 0" >>$path
            echo "ip = $gfs_ip" >> $path
        elif [[ $volume_status -eq 0 && $brick_num -ne $node_num ]];then
            echo "status = 1" >>$path
            echo "ip = $gfs_ip" >>$path
            echo "err_info_1 = $cluster_err_info" >>$path
            echo "check_method_1 = $cluster_check_method" >>$path
        else
            echo "status = 1" >>$path
            echo "ip = $gfs_ip" >>$path
            echo "err_info_1 = $volume_err_info" >>$path
            echo "check_method_1 = $volume_check_method" >>$path
        fi
    done
elif [ $gfs_num -ne 0 ];then
    echo "[gfs_$gfs_ips]" >>$path
    check_volume_status $gfs_ips
    if [ $volume_status -eq 0 ];then
        echo "status = 0" >>$path
        echo "ip = $gfs_ips" >>$path
    else
        echo "status = 1" >>$path
        echo "ip = $gfs_ips" >>$path
        echo "err_info_1 = $volume_err_info"  >>$path
        echo "check_method_1 = $volume_check_method" >> $path
    fi
fi    
