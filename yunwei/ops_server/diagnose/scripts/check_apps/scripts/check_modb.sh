#!/bin/bash
. /opt/data/luban/shells/kdfunctions
ip_info=$1
modb_ips=($(grep -w modb $ip_info | cut -d"=" -f 2))
# echo ${modb_ips[@]}
path=$3


check_role()
{
    ip=$1
    dms_status=$(curl -s -I http://${ip}:9200 | grep HTTP/1.0 | cut -d" " -f 2)
    proc_num=$(ssh -o StrictHostKeyChecking=no -p 33332 root@$ip ps aux | grep modb | egrep -v "modbcore|grep" | wc -l)
    if [[ $dms_status -eq 200 && $proc_num -eq 2 ]];then
        flag=0
    elif [[ $dms_status -eq 503 && $proc_num -eq 0 ]];then
        flag=10
    else
        flag=1
    fi
    role_err_info="modb is not running correctly"
    role_check_method="curl -s -I http://${ip}:9200 and ps aux | grep modb"
}


check_version()
{
    ip=$1
    last_modb_dat=`ssh -o StrictHostKeyChecking=no -p 33332 root@$ip tail -1 /opt/log/modb/modb_version.dat`
    last_modb_log=`ssh -o StrictHostKeyChecking=no -p 33332 root@$ip tail -1 /opt/log/modb/modb_version.log`
    echo $last_modb_log | grep "ERR"
    log_is_err=$?
    if [ $log_is_err -eq 0 ];then
        ver_flag=1
    else
        dat_ver=(`echo $last_modb_dat| awk '{print "bmcVer:"$1,$3}'`)
        log_ver=(`echo $last_modb_log| awk '{print $(NF-1),$NF}'`)
        log_ver_nf=`echo ${log_ver[1]} |awk -F"," '{print $NF}'`
        mysql_ver=(`/opt/midware/mysql/bin/mysql -h$ip -ukedacom -pKedaMysql16#  -e 'use modb_db;select bmc_version,modb_versions_from_msg from modbver order by bmc_version desc limit 1' 2>/dev/null | grep -v "bmc_version" | awk '{print "bmcVer:"$1,$2}'`)
        if [ "${dat_ver[0]}" == "${log_ver[0]}" ] && [ "$log_ver_nf" == "${dat_ver[1]}" ];then
            if [ "${dat_ver[0]}" == "${mysql_ver[0]}" ] && [ "${dat_ver[1]}" == "${mysql_ver[1]}" ];then
                ver_flag=0
            else
                ver_flag=1
            fi
        fi
    fi
    modb_err_info="modb_version.dat modb_version.log modb_db version not match"
    modb_check_method="check modb_version.dat、modb_version.log、modb_db data "
}

for modb_ip in ${modb_ips[@]};do
    echo "[modb_$modb_ip]" >>$path
    check_role $modb_ip
    if [ $flag -eq 0 ];then
        check_version $modb_ip
        if [ $ver_flag -eq 0 ];then
            echo "status = 0" >>$path
            echo "ip = $modb_ip" >>$path
        else
            echo "status = 1" >>$path
            echo "ip = $modb_ip" >>$path
            echo "err_info_1 = $modb_err_info" >>$path
            echo "check_method_1 = $modb_check_method" >>$path
        fi
    elif [ $flag -eq 10 ];then
        echo "status = 0" >>$path
        echo "ip = $modb_ip" >>$path
    else
        echo "status = 1" >>$path
        echo "ip = $modb_ip" >>$path
        echo "err_info_1 = $modb_err_info">>$path
        echo "check_method_1 = $modb_check_method" >>$path
    fi
done

