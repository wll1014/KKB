#!/bin/bash
. /opt/data/luban/shells/kdfunctions
ip_info=$1
mysql_ip=($(grep mysql $ip_info | cut -d"=" -f 2))
# echo ${mysql_ip[@]}
mysql_ha_port=3306
mysql_port=3316
path=$3

check_link_status()
{
    ip=$1
    /opt/midware/mysql/bin/mysql -ukedacom -pKedaMysql16# -h $ip -e "connect" 2>/dev/null
    link_status=$?
    link_err_info="connect 3306 failed"
    link_check_method="mysql -ukedacom -pKedaMysql16# -P3306"
}

check_database_num()
{
    ip=$1
    flag=0
    databases=(ap cert city_ip confinfodb dbupdateinfo kdvsm kdvvrs manager meeting modb_db movision mpcddb nms_db scheduledconfinfodb service ssu sus  tso wps)
    databases2=$(/opt/midware/mysql/bin/mysql  -h $ip -P3316 -ukedacom -pKedaMysql16# -e "show databases;" 2>/dev/null | grep -v "Database" | xargs)
    num=0
    for database in ${databases[@]};do
        if [[ "$databases2" =~ "${database}" ]];then
            # echo $database
            ((num++))
            continue
        else
            database_err_info="database missing ${database}" 
            check_database_method="use 'show database' compare databases"
            flag=1
            break
        fi
    done
}

check_slave_status()
{
    ip=$1
    num_yes=$(/opt/midware/mysql/bin/mysql -ukedacom -pKedaMysql16# -P3316 -h$ip -e "show slave status\G" 2>/dev/null | egrep -w "Slave_IO_Running|Slave_SQL_Running" | grep "Yes" | wc -l)
    slave_err_info="Slave_IO_Running or Slave_SQL_Running status is not Yes"
    check_slave_method="show slave status"
}


mysql_num=${#mysql_ip[@]}
if [ $mysql_num -eq 1 ];then
    echo "[mysql_${mysql_ip[@]}]">>$path
    check_link_status ${mysql_ip[@]}
    check_database_num ${mysql_ip[@]}
    if [ $link_status -eq 0 -a $flag -eq 0 ];then
        echo "status = 0" >>$path
        echo "ip = ${mysql_ip[@]}" >>$path
    elif [ $link_status -eq 0 -a $flag -eq 1 ];then
        echo "status = 1" >>$path
        echo "ip = ${mysql_ip[@]}" >>$path
        echo "err_info_1 = ${database_err_info}" >>$path
        echo "check_method_1 = ${check_database_method}" >>$path
    else
        echo "status = 1" >>$path
        echo "ip = ${mysql_ip[@]}" >>$path
        echo "err_info_1 = $link_err_info" >>$path
        echo "check_method_1 = $link_check_method" >>$path
    fi
elif [ $mysql_num -eq 2 ];then
    for my_ip in ${mysql_ip[@]};do
        echo "[mysql_${my_ip}]">>$path
        check_link_status $my_ip
        check_database_num $my_ip
        check_slave_status $my_ip
        if [ $link_status -eq 0 -a $flag -eq 0 -a $num_yes -eq 2 ];then
            echo "status = 0" >>$path
            echo "ip = $my_ip" >>$path            
        elif [ $link_status -eq 0 -a $flag -eq 0 -a $num_yes -ne 2 ];then
            echo "status = 1" >>$path
            echo "ip = $my_ip" >>$path
            echo "err_info_1 = $slave_err_info" >>$path
            echo "check_method_1 = $check_slave_method" >>$path
        elif [ $link_status -eq 0 -a $flag -ne 0 -a $num_yes -ne 2 ];then
            echo "status = 1" >>$path
            echo "ip = $my_ip" >>$path
            echo "err_info_1 = $slave_err_info" >>$path
            echo "check_method_1 = $check_slave_method" >>$path
            echo "err_info_2 = $database_err_info" >>$path
            echo "check_method_2 = $check_database_method" >>$path
        elif [ $link_status -eq 0 -a $flag -ne 0 -a $num_yes -eq 2 ];then
            echo "status = 1" >>$path
            echo "ip = $my_ip" >>$path
            echo "err_info_1 = $database_err_info" >>$path
            echo "check_method_1 = $check_database_method" >>$path
        else
            echo "status = 1" >>$path
            echo "ip = $my_ip" >>$path
            echo "err_info_1 = $link_err_info" >>$path
            echo "check_method_1 = $link_check_method" >>$path
        fi

    done



fi



