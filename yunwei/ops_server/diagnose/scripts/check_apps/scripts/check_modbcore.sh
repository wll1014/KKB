#!/bin/bash
. /opt/data/luban/shells/kdfunctions
ip_info=$1
modbcore_ips=($(grep -w modbcore $ip_info | cut -d"=" -f 2))
path=$3


check_status()
{
    ip=$1
    modbcore_moid=$(echo "/opt/midware/zookeeper/bin/zkCli.sh get /monitor_lock/domain/mooooooo-oooo-oooo-oooo-topplatfoorm/modbcore" |ssh -o StrictHostKeyChecking=no -p 33332 root@$ip 2>/dev/null | grep server_moid | awk -F"\"" '{print $4}' )
    if [ ! -z $modbcore_moid ];then
        moid_num=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$ip cat /opt/data/config/luban_config/deploy.json | grep $modbcore_moid | wc -l)
        proc_num=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$ip  ps aux | grep modbcore | grep -v grep | wc -l)
        if [ $moid_num -eq 1 -a $proc_num -eq 2 ];then
            flag=0
        elif [ $moid_num -eq 0 -a $proc_num -eq 0 ];then
            flag=10
        else
            flag=1
        fi
        modbcore_err_info="modbcore is not need start"
        modbcore_check_method="/opt/midware/zookeeper/bin/zkCli.sh get /monitor_lock/domain/mooooooo-oooo-oooo-oooo-topplatfoorm/modbcore"
    else
        flag=1
        modbcore_err_info="modbcore is not create monitor_lock"
        modbcore_check_method="/opt/midware/zookeeper/bin/zkCli.sh get /monitor_lock/domain/mooooooo-oooo-oooo-oooo-topplatfoorm/modbcore"
    fi
}


check_version()
{
    ip=$1
    last_modbcore_log=(`ssh -o StrictHostKeyChecking=no -p 33332 root@$ip cat /opt/log/modbcore/modbcore.log |grep Success|grep modbVer | tail -1 | awk -F"[()]" '{print $4}' | awk -F"," '{gsub("\"","");print $1,$2}'`)
    last_mysql_dat=(`/opt/midware/mysql/bin/mysql -h$ip -ukedacom -pKedaMysql16#  -e 'use modb_db;select bmc_version,modb_versions_from_msg from modbver order by bmc_version desc limit 1' 2>/dev/null | grep -v "bmc_version" | awk '{print $1,$2}'`)
    if [ x"${last_modbcore_log[0]}" == x"${last_mysql_dat[0]}" ] && [ x"${last_modbcore_log[1]}" == x"${last_mysql_dat[1]}" ];then
        ver_flag=0
    else
        ver_flag=1
    fi
    ver_err_info="modb_db modb_version.log data not match"
    ver_check_method="compare modb_version.log with modb_db database"
}


 for modbcore_ip in ${modbcore_ips[@]};do
    echo "[modbcore_$modbcore_ip]" >>$path
    check_status $modbcore_ip
    if [ $flag -eq 0 ];then
        check_version $modbcore_ip
        if [ $ver_flag -eq 0 ];then
            echo "status = 0" >>$path
            echo "ip = $modbcore_ip" >>$path
        else
            echo "status = 1" >>$path
            echo "ip = $modbcore_ip" >>$path
            echo "err_info_1 = $ver_err_info" >>$path
            echo "check_method_1 = $ver_check_method" >>$path
        fi
    elif [ $flag -eq 10 ];then
        echo "status = 0" >>$path
        echo "ip = $modbcore_ip" >>$path
    else
        echo "status = 1" >>$path
        echo "ip = $modbcore_ip" >>$path
        echo "err_info_1 = $modbcore_err_info">>$path
        echo "check_method_1 = $modbcore_check_method" >>$path
    fi
done